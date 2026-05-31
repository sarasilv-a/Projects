import socket
import time
import threading
import random
from collections import deque

from config import UDP_PORT

from protocols.control_types import MessageType, ControlSubtype
from protocols.heartbeat_packet import HeartbeatPing, HeartbeatPong
from protocols.neighbor_control_packet import NeighborControlPacket, LeavePacket
from protocols.flooding_packet import FloodingPacket
from protocols.ack_packet import AckPacket
from protocols.route_withdraw_packet import RouteWithdrawPacket
from protocols.stream_list_packet import StreamListRequestPacket
from protocols.stream_request_packet import StreamRequestPacket, StreamResponseMessage, RequestMethod
from protocols.rtp_packet import RtpPacket
from protocols.nack_packet import NackPacket
from streams.stream_session_packet import StreamSessionPacket

from transport.heartbeat import HeartbeatManager
from transport.routing import RoutingManager
from transport.streaming import StreamingManager
from transport.reliable_ctrl import ReliableControlManager

class Node:
    def __init__(self, config):
        self.node_id = config["id"]
        self.role = config.get("role")
        self.neighbors = config.get("neighbors", [])

        # UDP socket
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(("0.0.0.0", UDP_PORT))

        # ---------- LOCKS & HEARTBEAT STATE ----------
        self._lock = threading.RLock()
        self._hb_state = {}
        # último RTT em ms por vizinho
        self.last_rtt = {}
        # pings pendentes: (ip, ping_id) -> ts
        self._pending_pings = {}
        self._ping_lock = threading.Lock()

        # ---------- FLOODING / ROUTING ----------
        self.FLOW_EXPECTED_PER_BURST = 5
        self.FLOW_BURST_TIMEOUT = 0.1

        # (from_ip, flow_id) -> {...}
        self.flow_state = {}
        self._flows_lock = threading.Lock()

        # routing_table: stream_id -> { server_id, next_hop, rtt_ms, loss_pct, cost }
        self.routing_table = {}

        # neighbor_history[flow_id][neighbor_ip] = deque([...])
        self.neighbor_history = {}

        # flow_id -> {"rtt_ms":..., "loss_pct":..., "cost":...}
        self.best_flow_metric = {}

        # nós recentemente mortos -> ignorar PING/ANNOUNCE até timestamp
        # ip -> ignore_until
        self.dead_cooldown = {}

        # controlo fiável genérico
        self._pending_control = {}
        self._pending_lock = threading.Lock()

        # cooldown por (vizinho, stream_id) depois de ROUTE_WITHDRAW
        # (remote_ip, stream_id) -> ignore_until
        self.recent_withdraws = {}

        # ---------- STREAMING ----------
        # stream_id -> StreamSessionPacket
        self.local_streams = {}

        # stream_id -> { client_ip -> { paused: bool } }
        self.stream_clients = {}

        # stream_id -> { "active": bool, "next_hop": str }
        self.stream_upstreams = {}

        # req_id -> {"response": StreamResponseMessage | None}
        self.pending_requests = {}
        self._requests_lock = threading.Lock()

        # Lock para acesso a estruturas de stream
        self._streams_lock = threading.Lock()

        # history de pacotes enviados downstream
        # (stream_id, remote_ip) -> {"packets": {seq: pkt}, "order": [seq,...]}
        self.rtx_history = {}
        self.RTX_HISTORY_MAX = 200

        # estado de recepção RTP por link upstream
        # (upstream_ip, stream_id) -> {"last_seq":..., "expected":..., "received":...}
        self.rtp_rx_state = {}

        # threshold de perda (5%)
        self.LOSS_THRESHOLD = 0.05

        # ---------- MANAGERS ----------
        self.heartbeat = HeartbeatManager(self)
        self.routing = RoutingManager(self)
        self.streaming = StreamingManager(self)
        self.reliable = ReliableControlManager(self)

    # ------------------------------------------------------------------
    # MAIN RUN
    # ------------------------------------------------------------------
    def run(self):
        threading.Thread(target=self.udp_loop, daemon=True).start()
        threading.Thread(target=self.heartbeat.loop, daemon=True).start()
        threading.Thread(target=self.streaming.stream_loop, daemon=True).start()
        threading.Thread(target=self.routing.flow_cleanup_loop, daemon=True).start()

        while True:
            print("\n==== NODE", self.node_id, "====")
            print("Routing table:")
            for sid, info in self.routing_table.items():
                print(
                    f"  {sid} -> next_hop={info['next_hop']}, "
                    f"rtt={info['rtt_ms']:.3f} ms, loss={info['loss_pct']:.3f} %, "
                    f"cost={info['cost']:.3f}"
                )

            print("Last RTTs (PING/PONG) (ms):")
            for ip, rtt in self.last_rtt.items():
                print(f"  {ip}: {rtt:.3f} ms")

            time.sleep(5)

    # ------------------------------------------------------------------
    # UDP LOOP
    # ------------------------------------------------------------------
    def udp_loop(self):
        while True:
            try:
                data, addr = self.udp_sock.recvfrom(65535)
                remote_ip, remote_port = addr
            except OSError as e:
                print(f"[{self.node_id}] Error in udp_loop recv: {e}")
                time.sleep(0.1)
                continue

            if not data:
                continue

            tipo = data[0]

            if tipo == MessageType.CONTROL:
                if len(data) < 2:
                    continue
                subtipo = data[1]

                if subtipo in (ControlSubtype.JOIN, ControlSubtype.LEAVE):
                    try:
                        msg = NeighborControlPacket.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid JOIN/LEAVE from {remote_ip}: {e}")
                        continue
                    self.heartbeat.handle_join_leave(remote_ip, msg)

                elif subtipo == ControlSubtype.ACK:
                    try:
                        ack = AckPacket.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid ACK from {remote_ip}: {e}")
                        continue
                    self.reliable.handle_ack(remote_ip, ack)

                elif subtipo == ControlSubtype.ANNOUNCE:
                    try:
                        msg = FloodingPacket.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid ANNOUNCE from {remote_ip}: {e}")
                        continue
                    self.routing.handle_announce(remote_ip, msg)

                elif subtipo == ControlSubtype.PING:
                    try:
                        ping = HeartbeatPing.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid PING from {remote_ip}: {e}")
                        continue
                    self.heartbeat.handle_ping(remote_ip, ping)

                elif subtipo == ControlSubtype.PONG:
                    try:
                        pong = HeartbeatPong.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid PONG from {remote_ip}: {e}")
                        continue
                    self.heartbeat.handle_pong(remote_ip, pong)

                elif subtipo == ControlSubtype.ROUTE_WITHDRAW:
                    try:
                        rw = RouteWithdrawPacket.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid ROUTE_WITHDRAW from {remote_ip}: {e}")
                        continue
                    self.routing.handle_route_withdraw(remote_ip, rw)

                elif subtipo == ControlSubtype.REQUEST:
                    try:
                        req = StreamRequestPacket.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid REQUEST from {remote_ip}: {e}")
                        continue

                    # ACK do REQUEST (fiável)
                    try:
                        ack = AckPacket(orig_subtype=ControlSubtype.REQUEST, msg_id=req.req_id)
                        self.udp_sock.sendto(ack.serialize(), (remote_ip, UDP_PORT))
                    except OSError as e:
                        print(f"[{self.node_id}] Error sending ACK(REQUEST) to {remote_ip}: {e}")

                    self.streaming.handle_stream_request(remote_ip, req)

                elif subtipo == ControlSubtype.RESPONSE:
                    try:
                        resp = StreamResponseMessage.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid RESPONSE from {remote_ip}: {e}")
                        continue

                    self.streaming.handle_stream_response(resp, addr)

                elif subtipo == ControlSubtype.STREAM_LIST_REQUEST:
                    try:
                        list_req = StreamListRequestPacket.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid STREAM_LIST_REQUEST from {remote_ip}: {e}")
                        continue

                    self.streaming.handle_stream_list_request(remote_ip, list_req)

                elif subtipo == ControlSubtype.NACK:
                    try:
                        nack = NackPacket.deserialize(data)
                    except Exception as e:
                        print(f"[{self.node_id}] Invalid NACK from {remote_ip}: {e}")
                        continue

                    self.streaming.handle_nack(remote_ip, nack)

                else:
                    print(
                        f"[{self.node_id}] CONTROL message with subtype={subtipo} ignored on UDP"
                    )

            elif tipo == MessageType.STREAM:
                self.streaming.handle_stream_packet(remote_ip, data)

            else:
                print(f"[{self.node_id}] Unknown UDP message type={tipo} from {remote_ip}")
