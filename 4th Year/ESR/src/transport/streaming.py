import time
import threading
from typing import TYPE_CHECKING

from config import UDP_PORT
from protocols.stream_list_packet import StreamListRequestPacket, StreamListResponsePacket
from protocols.stream_request_packet import (
    StreamRequestPacket,
    StreamResponseMessage,
    RequestMethod,
)
from protocols.rtp_packet import RtpPacket
from protocols.nack_packet import NackPacket
from streams.stream_session_packet import StreamSessionPacket
from protocols.control_types import ControlSubtype

if TYPE_CHECKING:
    from transport.node import Node


class StreamingManager:
    def __init__(self, node: "Node"):
        self.node = node

    # ---------------- STREAM LIST ----------------
    def handle_stream_list_request(self, remote_ip: str, req: StreamListRequestPacket):
        entries = []

        for sid, info in self.node.routing_table.items():
            server_id = info.get("server_id", "")
            entries.append((sid, server_id))

        resp = StreamListResponsePacket(req.req_id, entries)

        try:
            self.node.udp_sock.sendto(resp.serialize(), (remote_ip, UDP_PORT))
            print(
                f"[{self.node.node_id}] STREAM_LIST_RESPONSE enviado para {remote_ip} "
                f"com {len(entries)} entradas (req_id={req.req_id})"
            )
        except OSError as e:
            print(
                f"[{self.node.node_id}] erro ao enviar STREAM_LIST_RESPONSE para "
                f"{remote_ip}:{UDP_PORT}: {e}"
            )

    # ---------------- REQUEST / RESPONSE ----------------
    def handle_stream_request(self, remote_ip: str, req: StreamRequestPacket):
        client_ip = remote_ip
        stream_id = req.stream_id

        print(
            f"[{self.node.node_id}] UDP REQUEST {req.method} "
            f"from {client_ip} for stream {stream_id}"
        )

        if req.method == RequestMethod.PLAY:
            if stream_id not in self.node.stream_clients:
                self.node.stream_clients[stream_id] = {}
            self.node.stream_clients[stream_id][client_ip] = {"paused": False}

            status = 0
            msg = "OK"

            if stream_id not in self.node.local_streams:
                next_hop = self.node.routing_table.get(stream_id, {}).get("next_hop")

                if not next_hop or next_hop == client_ip:
                    print(
                        f"[{self.node.node_id}] No SAFE route for stream {stream_id} "
                        f"(next_hop={next_hop}, client={client_ip})"
                    )
                    status = 1
                    msg = "No route for stream"
                else:
                    if stream_id not in self.node.stream_upstreams:
                        if stream_id not in self.node.local_streams:
                            self.node.local_streams[stream_id] = StreamSessionPacket(stream_id)

                        self.node.stream_upstreams[stream_id] = {
                            "active": True,
                            "next_hop": next_hop,
                        }
                        threading.Thread(
                            target=self._request_stream_from_upstream,
                            args=(stream_id, next_hop),
                            daemon=True,
                        ).start()

            resp = StreamResponseMessage(req.req_id, status, msg)
            try:
                self.node.udp_sock.sendto(resp.serialize(), (client_ip, UDP_PORT))
            except OSError as e:
                print(
                    f"[{self.node.node_id}] Error sending RESPONSE to {client_ip}: {e}"
                )
            return

        elif req.method == RequestMethod.PAUSE:
            if (
                stream_id in self.node.stream_clients
                and client_ip in self.node.stream_clients[stream_id]
            ):
                self.node.stream_clients[stream_id][client_ip]["paused"] = True
                status = 0
                msg = "PAUSED"
            else:
                status = 1
                msg = "Client not subscribed"

            resp = StreamResponseMessage(req.req_id, status, msg)
            try:
                self.node.udp_sock.sendto(resp.serialize(), (client_ip, UDP_PORT))
            except OSError as e:
                print(
                    f"[{self.node.node_id}] Error sending RESPONSE(PAUSE) to {client_ip}: {e}"
                )
            return

        elif req.method == RequestMethod.TEARDOWN:
            if stream_id in self.node.stream_clients:
                self.node.stream_clients[stream_id].pop(client_ip, None)

            resp = StreamResponseMessage(req.req_id, 0, "TEARDOWN")
            try:
                self.node.udp_sock.sendto(resp.serialize(), (client_ip, UDP_PORT))
            except OSError as e:
                print(
                    f"[{self.node.node_id}] Error sending RESPONSE(TEARDOWN) to {client_ip}: {e}"
                )

            if (
                stream_id in self.node.stream_upstreams
                and len(self.node.stream_clients.get(stream_id, {})) == 0
            ):
                upstream = self.node.stream_upstreams[stream_id]["next_hop"]
                threading.Thread(
                    target=self._send_teardown_upstream,
                    args=(stream_id, upstream),
                    daemon=True,
                ).start()

            return

        else:
            resp = StreamResponseMessage(req.req_id, 1, "Unknown method")
            try:
                self.node.udp_sock.sendto(resp.serialize(), (client_ip, UDP_PORT))
            except OSError as e:
                print(
                    f"[{self.node.node_id}] Error sending RESPONSE(UNKNOWN) to {client_ip}: {e}"
                )

    def handle_stream_response(self, resp: StreamResponseMessage, addr):
        with self.node._requests_lock:
            if resp.req_id in self.node.pending_requests:
                self.node.pending_requests[resp.req_id]["response"] = resp

        remote_ip = addr[0]
        with self.node._pending_lock:
            self.node._pending_control.pop((remote_ip, resp.req_id), None)

    # ---------------- STREAM PACKETS & NACK ----------------
    def handle_stream_packet(self, remote_ip: str, data: bytes):
        if len(data) < 2:
            return

        sid_len = data[1]
        if len(data) < 2 + sid_len + 1:
            return

        stream_id = data[2 : 2 + sid_len].decode("utf-8")
        rtp_bytes = data[2 + sid_len :]

        rtp = RtpPacket()
        try:
            rtp.decode(rtp_bytes)
        except Exception as e:
            print(
                f"[{self.node.node_id}] RTP decode error from {remote_ip} "
                f"(stream {stream_id}): {e}"
            )
            return

        seq = rtp.seqNum()

        # --------- RTP RX STATE (por upstream + stream) ---------
        key = (remote_ip, stream_id)
        st = self.node.rtp_rx_state.get(key)
        if st is None:
            WARMUP_PKTS = 20
            st = {"last_seq": None, "expected": 0, "received": 0, "warmup": WARMUP_PKTS}
            self.node.rtp_rx_state[key] = st

        if st["last_seq"] is None:
            st["last_seq"] = seq
            st["expected"] = 1
            st["received"] = 1

            # conta warm-up (um pacote recebido)
            if st.get("warmup", 0) > 0:
                st["warmup"] -= 1
        else:
            delta = seq - st["last_seq"]
            if delta > 0:
                st["expected"] += delta
                st["received"] += 1

                # conta warm-up (um pacote recebido)
                if st.get("warmup", 0) > 0:
                    st["warmup"] -= 1

                if delta > 1:
                    if st.get("warmup", 0) > 0:
                        st["last_seq"] = seq
                    else:
                        missing_first = st["last_seq"] + 1
                        missing_last = seq - 1
                        loss_pct = (st["expected"] - st["received"]) / max(1, st["expected"])

                        print(
                            f"[{self.node.node_id}] Upstream {remote_ip} stream={stream_id}: "
                            f"delta={delta}, loss_est={loss_pct*100:.2f}%"
                        )

                        if loss_pct >= self.node.LOSS_THRESHOLD:
                            nack = NackPacket(stream_id, missing_first, missing_last)
                            try:
                                self.node.udp_sock.sendto(nack.serialize(), (remote_ip, UDP_PORT))
                                print(
                                    f"[{self.node.node_id}] NACK -> {remote_ip} stream={stream_id} "
                                    f"seq=[{missing_first},{missing_last}]"
                                )
                            except OSError as e:
                                print(
                                    f"[{self.node.node_id}] erro ao enviar NACK para {remote_ip}: {e}"
                                )

                        st["last_seq"] = seq
                else:
                    st["last_seq"] = seq

        # --------- Encaminhamento para sessão (active) ou buffer (pending) ---------
        with self.node._streams_lock:
            upstream_info = self.node.stream_upstreams.get(stream_id)
            if not upstream_info or not upstream_info.get("active"):
                return

            active = upstream_info.get("next_hop")
            pending = upstream_info.get("pending_next_hop")

            # pacote do upstream ativo -> entra direto na sessão
            if remote_ip == active:
                session = self.node.local_streams.get(stream_id)
                if session:
                    session.push_packet(data)
                return

            # pacote do upstream pendente -> vai para buffer (graceful switch)
            if pending and remote_ip == pending:
                buf = upstream_info.setdefault("pending_buffer", [])
                buf.append(data)

                # limita buffer para não rebentar memória
                if len(buf) > 300:
                    del buf[: len(buf) - 300]
                return

            # qualquer outro -> ignora
            return

    def handle_nack(self, remote_ip: str, nack: NackPacket):
        key = (nack.stream_id, remote_ip)
        hist = self.node.rtx_history.get(key)

        if not hist:
            print(
                f"[{self.node.node_id}] NACK: sem history para stream={nack.stream_id} "
                f"-> {remote_ip}"
            )
            return

        print(
            f"[{self.node.node_id}] NACK de {remote_ip} para stream={nack.stream_id} "
            f"seq=[{nack.first_seq},{nack.last_seq}]"
        )

        for seq in range(nack.first_seq, nack.last_seq + 1):
            pkt = hist["packets"].get(seq)
            if pkt:
                try:
                    self.node.udp_sock.sendto(pkt, (remote_ip, UDP_PORT))
                    print(
                        f"[{self.node.node_id}] Retransmit seq={seq} "
                        f"stream={nack.stream_id} -> {remote_ip}"
                    )
                except OSError as e:
                    print(
                        f"[{self.node.node_id}] erro ao retransmitir seq={seq} "
                        f"para {remote_ip}: {e}"
                    )

    # ---------------- RELIABLE REQUEST HELPERS ----------------
    def _wait_for_response(self, req_id: int, timeout_total: float = 2.0):
        resp = None
        deadline = time.time() + timeout_total
        while time.time() < deadline:
            with self.node._requests_lock:
                entry = self.node.pending_requests.get(req_id)
                if entry and entry.get("response") is not None:
                    resp = entry["response"]
                    break
            time.sleep(0.05)
        return resp

    def _send_stream_request(self, dest_ip: str, stream_id: str, method: int):
        req_id = int(time.time() * 1000) % (2**32)
        req = StreamRequestPacket(
            req_id=req_id,
            client_id=self.node.node_id,
            stream_id=stream_id,
            method=method,
        )

        payload = req.serialize()

        with self.node._requests_lock:
            self.node.pending_requests[req_id] = {"response": None}

        ack_ok = self.node.reliable.send_with_retries(
            payload, req_id, dest_ip, ControlSubtype.REQUEST
        )
        resp = None
        if ack_ok:
            resp = self._wait_for_response(req_id)

        with self.node._requests_lock:
            self.node.pending_requests.pop(req_id, None)

        return ack_ok, resp

    # ---------------- STREAM PACKET HELPERS ----------------
    def _request_stream_from_upstream(self, stream_id, next_hop):
        print(
            f"[{self.node.node_id}] Requesting stream {stream_id} from upstream {next_hop}"
        )

        ack_ok, resp = self._send_stream_request(next_hop, stream_id, RequestMethod.PLAY)

        if resp is None:
            print(
                f"[{self.node.node_id}] No RESPONSE for stream request {stream_id} "
                f"from {next_hop}"
            )
            return

        if not ack_ok:
            print(
                f"[{self.node.node_id}] REQUEST PLAY not ACKed by {next_hop} "
                f"(stream {stream_id})"
            )
            return

        if resp.status != 0:
            print(
                f"[{self.node.node_id}] Upstream {next_hop} refused stream {stream_id}: "
                f"{resp.message}"
            )
            return

        print(f"[{self.node.node_id}] Upstream accepted stream {stream_id}")

        with self.node._streams_lock:
            if stream_id in self.node.local_streams:
                pass

        threading.Thread(
            target=self._receive_stream_from_upstream,
            args=(stream_id,),
            daemon=True,
        ).start()

    def _receive_stream_from_upstream(self, stream_id):
        print(
            f"[{self.node.node_id}] _receive_stream_from_upstream called for {stream_id} "
            f"(actual receiving is done in udp_loop)"
        )

    def _send_teardown_upstream(self, stream_id, next_hop, cleanup=True):
        ack_ok, resp = self._send_stream_request(
            next_hop, stream_id, RequestMethod.TEARDOWN
        )

        if not ack_ok:
            print(
                f"[{self.node.node_id}] TEARDOWN not ACKed by {next_hop} "
                f"for stream {stream_id}"
            )
        elif resp is not None:
            print(
                f"[{self.node.node_id}] TEARDOWN response from {next_hop}: "
                f"status={resp.status} msg={resp.message}"
            )

        with self.node._streams_lock:
            info = self.node.stream_upstreams.get(stream_id)

            if cleanup and info and info.get("next_hop") == next_hop:
                self.node.stream_upstreams.pop(stream_id, None)
                self.node.local_streams.pop(stream_id, None)
                print(
                    f"[{self.node.node_id}] Cleaned up stream state for {stream_id}"
                )
            else:
                print(
                    f"[{self.node.node_id}] Skipping cleanup for {stream_id} "
                    f"(next_hop={next_hop}, cleanup={cleanup})"
                )

    # ---------------- STREAM LOOP ----------------
    def stream_loop(self):
        print(f"[{self.node.node_id}] Stream relay loop started")

        READY_N = 30

        while True:
            time.sleep(0.01)

            with self.node._streams_lock:
                for stream_id, clients_dict in list(self.node.stream_clients.items()):
                    if not clients_dict:
                        continue

                    active_clients = [
                        client_ip
                        for client_ip, client_info in clients_dict.items()
                        if not client_info.get("paused", False)
                    ]
                    if not active_clients:
                        continue

                    route = self.node.routing_table.get(stream_id)
                    upstream_info = self.node.stream_upstreams.get(stream_id)

                    # se não existe upstream ainda, nada a fazer aqui
                    if not upstream_info:
                        continue

                    # 1) Se houver pending e buffer já estiver pronto -> commit + teardown antigo
                    pending = upstream_info.get("pending_next_hop")
                    buf = upstream_info.get("pending_buffer", [])

                    if pending and len(buf) >= READY_N:
                        old = upstream_info.get("next_hop")

                        print(
                            f"[{self.node.node_id}] Graceful switch commit for {stream_id}: "
                            f"{old} -> {pending} (buffer={len(buf)})"
                        )

                        # Injeta buffer na sessão para os clientes não sentirem corte
                        session = self.node.local_streams.get(stream_id)
                        if session:
                            for pkt in buf:
                                session.push_packet(pkt)

                        # Troca upstream ativo
                        upstream_info["next_hop"] = pending
                        upstream_info.pop("pending_next_hop", None)
                        upstream_info.pop("pending_buffer", None)

                        # Teardown do antigo só depois do commit
                        if old:
                            threading.Thread(
                                target=self._send_teardown_upstream,
                                args=(stream_id, old, False),
                                daemon=True,
                            ).start()

                    # 2) Se a rota mudou -> iniciar pending (sem matar o stream atual)
                    if route and upstream_info:
                        best_next_hop = route.get("next_hop")
                        current_next_hop = upstream_info.get("next_hop")

                        if best_next_hop and best_next_hop != current_next_hop:
                            # Se já estamos a preparar switch para este best_next_hop, não reiniciar
                            if upstream_info.get("pending_next_hop") != best_next_hop:
                                print(
                                    f"[{self.node.node_id}] Graceful switch start for {stream_id}: "
                                    f"{current_next_hop} -> {best_next_hop}"
                                )

                                upstream_info["pending_next_hop"] = best_next_hop
                                upstream_info["pending_buffer"] = []

                                if stream_id not in self.node.local_streams:
                                    self.node.local_streams[stream_id] = StreamSessionPacket(stream_id)

                                threading.Thread(
                                    target=self._request_stream_from_upstream,
                                    args=(stream_id, best_next_hop),
                                    daemon=True,
                                ).start()

                    # 3) Reencaminhar pacotes para clientes
                    session = self.node.local_streams.get(stream_id)
                    if not session:
                        continue

                    packet = session.get_next_packet()
                    if not packet:
                        continue

                    if len(packet) < 2:
                        continue
                    sid_len = packet[1]
                    if len(packet) < 2 + sid_len + 1:
                        continue

                    rtp_bytes = packet[2 + sid_len :]
                    rtp = RtpPacket()
                    try:
                        rtp.decode(rtp_bytes)
                    except Exception as e:
                        print(f"[{self.node.node_id}] RTP decode error ao reenviar: {e}")
                        continue

                    seq = rtp.seqNum()

                    for client_ip in active_clients:
                        key = (stream_id, client_ip)
                        hist = self.node.rtx_history.setdefault(
                            key, {"packets": {}, "order": []}
                        )
                        hist["packets"][seq] = packet
                        hist["order"].append(seq)
                        if len(hist["order"]) > self.node.RTX_HISTORY_MAX:
                            oldest = hist["order"].pop(0)
                            hist["packets"].pop(oldest, None)

                        try:
                            self.node.udp_sock.sendto(packet, (client_ip, UDP_PORT))
                            print(
                                f"[{self.node.node_id}] Sent RTP packet for stream "
                                f"{stream_id} to {client_ip}"
                            )
                        except OSError as e:
                            print(
                                f"[{self.node.node_id}] Error sending RTP to {client_ip}: {e}"
                            )

