import time
import random
import threading
from typing import TYPE_CHECKING

from config import UDP_PORT
from protocols.heartbeat_packet import HeartbeatPing, HeartbeatPong
from protocols.neighbor_control_packet import NeighborControlPacket, LeavePacket
from protocols.ack_packet import AckPacket
from protocols.control_types import MessageType, ControlSubtype

if TYPE_CHECKING:
    from transport.node import Node


class HeartbeatManager:
    def __init__(self, node: "Node"):
        self.node = node

    # ---------------- JOIN / LEAVE ----------------
    def handle_join_leave(self, remote_ip: str, msg: NeighborControlPacket):
        if msg.subtipo == ControlSubtype.JOIN:
            with self.node._lock:
                if remote_ip not in self.node.neighbors:
                    self.node.neighbors.append(remote_ip)
                self.node._hb_state[remote_ip] = {
                    "missed": 0,
                    "last_pong": time.time(),
                }
            print(f"[{self.node.node_id}] JOIN from {remote_ip}")

        elif msg.subtipo == ControlSubtype.LEAVE:
            print(f"[{self.node.node_id}] LEAVE from {remote_ip}")
            self._remove_neighbor(remote_ip)

        ack = AckPacket(orig_subtype=msg.subtipo, msg_id=msg.msg_id)
        try:
            self.node.udp_sock.sendto(ack.serialize(), (remote_ip, UDP_PORT))
        except OSError as e:
            print(f"[{self.node.node_id}] Error sending ACK to {remote_ip}: {e}")

    # ---------------- PING / PONG ----------------
    def handle_ping(self, remote_ip: str, ping: HeartbeatPing):
        now = time.time()
        with self.node._lock:
            ignore_until = self.node.dead_cooldown.get(remote_ip)

        if ignore_until is not None and now < ignore_until:
            print(
                f"[{self.node.node_id}] Ignoring PING from {remote_ip} "
                f"(dead cooldown active)"
            )
            return
        elif ignore_until is not None:
            with self.node._lock:
                self.node.dead_cooldown.pop(remote_ip, None)

        with self.node._lock:
            if remote_ip not in self.node.neighbors:
                print(f"[{self.node.node_id}] Adding {remote_ip} as neighbor due to PING")
                self.node.neighbors.append(remote_ip)

            st = self.node._hb_state.get(remote_ip)
            if st is None:
                st = {"missed": 0, "last_pong": time.time()}
                self.node._hb_state[remote_ip] = st
            else:
                st["missed"] = 0
                st["last_pong"] = time.time()

        pong = HeartbeatPong(ping.ping_id)
        try:
            self.node.udp_sock.sendto(pong.serialize(), (remote_ip, UDP_PORT))
        except OSError as e:
            print(f"[{self.node.node_id}] Error sending PONG to {remote_ip}: {e}")

    def handle_pong(self, remote_ip: str, pong: HeartbeatPong):
        key = (remote_ip, pong.ping_id)
        now = time.time()

        with self.node._ping_lock:
            sent_ts = self.node._pending_pings.pop(key, None)

        if sent_ts is None:
            print(
                f"[{self.node.node_id}] PONG from {remote_ip} with unknown ping_id={pong.ping_id}"
            )
            return

        rtt_ms = (now - sent_ts) * 1000.0
        self.node.last_rtt[remote_ip] = rtt_ms

        with self.node._lock:
            st = self.node._hb_state.get(remote_ip)
            if st is None:
                st = {"missed": 0, "last_pong": now}
                self.node._hb_state[remote_ip] = st
            else:
                st["missed"] = 0
                st["last_pong"] = now

        print(
            f"[{self.node.node_id}] RTT to {remote_ip}: {rtt_ms:.2f} ms "
            f"(ping_id={pong.ping_id})"
        )

    # ---------------- HEARTBEAT LOOP ----------------
    def loop(self):
        HEARTBEAT_INTERVAL = 3.0
        MAX_MISSED = 5

        while True:
            with self.node._lock:
                neighbor_ips = list(self.node.neighbors)

            for ip in neighbor_ips:
                with self.node._lock:
                    st = self.node._hb_state.get(ip)
                    if st is None:
                        st = {"missed": 0, "last_pong": time.time()}
                        self.node._hb_state[ip] = st

                ping_id = random.randint(1, 2**31 - 1)
                msg = HeartbeatPing(ping_id)

                send_ts = time.time()
                key = (ip, ping_id)
                with self.node._ping_lock:
                    self.node._pending_pings[key] = send_ts

                try:
                    self.node.udp_sock.sendto(msg.serialize(), (ip, UDP_PORT))
                    with self.node._lock:
                        st = self.node._hb_state.get(ip)
                        if st is not None:
                            st["missed"] += 1
                except OSError as e:
                    print(
                        f"[{self.node.node_id}] UDP send PING error to {ip}:{UDP_PORT}: {e}"
                    )
                    with self.node._ping_lock:
                        self.node._pending_pings.pop(key, None)
                    with self.node._lock:
                        st = self.node._hb_state.get(ip)
                        if st is not None:
                            st["missed"] += 1

            to_remove = []
            with self.node._lock:
                for ip in neighbor_ips:
                    st = self.node._hb_state.get(ip)
                    if st is not None and st["missed"] >= MAX_MISSED:
                        to_remove.append(ip)

            for ip in to_remove:
                with self.node._lock:
                    rtt_ms = self.node.last_rtt.get(ip)

                if rtt_ms is not None and rtt_ms > 0:
                    cooldown_ms = 3.0 * rtt_ms
                else:
                    cooldown_ms = 3.0 * HEARTBEAT_INTERVAL * 1000.0

                ignore_until = time.time() + (cooldown_ms / 1000.0)
                with self.node._lock:
                    self.node.dead_cooldown[ip] = ignore_until

                print(
                    f"[{self.node.node_id}] Neighbor {ip} considered DEAD "
                    f"(missed {MAX_MISSED} heartbeats) — "
                    f"ignoring PING/ANNOUNCE for ~{cooldown_ms:.3f} ms"
                )

                self._remove_neighbor(ip)

            time.sleep(HEARTBEAT_INTERVAL)

    # ---------------- HELPERS ----------------
    def ping_timeout(self, ip: str, factor: float = 1.0, default_ms: float = 1000.0) -> float:
        with self.node._lock:
            rtt_ms = self.node.last_rtt.get(ip)

        if rtt_ms is None or rtt_ms <= 0:
            return default_ms / 1000.0

        timeout_ms = factor * rtt_ms
        timeout_ms = max(50.0, min(5000.0, timeout_ms))
        return timeout_ms / 1000.0

    def _remove_neighbor(self, ip: str):
        removed_streams = []
        with self.node._lock:
            if ip in self.node.neighbors:
                self.node.neighbors.remove(ip)
            self.node._hb_state.pop(ip, None)
            self.node.last_rtt.pop(ip, None)

            for flow_id, fmap in list(self.node.neighbor_history.items()):
                fmap.pop(ip, None)
                if not fmap:
                    self.node.neighbor_history.pop(flow_id, None)

            for sid, info in list(self.node.routing_table.items()):
                if info.get("next_hop") == ip:
                    self.node.routing_table.pop(sid, None)
                    removed_streams.append(sid)

        with self.node._flows_lock:
            for (from_ip, flow_id) in list(self.node.flow_state.keys()):
                if from_ip == ip:
                    self.node.flow_state.pop((from_ip, flow_id), None)

        with self.node._ping_lock:
            to_del = [key for key in self.node._pending_pings.keys() if key[0] == ip]
            for key in to_del:
                self.node._pending_pings.pop(key, None)

        if removed_streams:
            self.node.routing.propagate_route_withdraw(removed_streams, origin_ip=ip)

        print(f"[{self.node.node_id}] Neighbor {ip} removed (dead or LEAVE)")
