import time
import os

from config import UDP_PORT
from streams.stream_session_packet import StreamSessionPacket

from protocols.neighbor_control_packet import NeighborControlPacket
from protocols.ack_packet import AckPacket
from protocols.control_types import MessageType, ControlSubtype
from protocols.heartbeat_packet import HeartbeatPing, HeartbeatPong
from protocols.stream_request_packet import StreamRequestPacket, StreamResponseMessage, RequestMethod
from protocols.route_withdraw_packet import RouteWithdrawPacket
from protocols.nack_packet import NackPacket


class ServerNetLoop:
    def __init__(self, server):
        self.s = server

    def udp_loop(self):
        s = self.s
        while True:
            try:
                data, addr = s.udp_sock.recvfrom(65535)
                remote_ip = addr[0]
            except:
                continue

            if not data:
                continue

            tipo = data[0]

            if tipo != MessageType.CONTROL:
                continue

            if len(data) < 2:
                continue

            subtipo = data[1]

            # JOIN/LEAVE -> ACK
            if subtipo in (ControlSubtype.JOIN, ControlSubtype.LEAVE):
                try:
                    msg = NeighborControlPacket.deserialize(data)
                except Exception as e:
                    print(f"[{s.node_id}] JOIN/LEAVE inválido de {remote_ip}: {e}")
                    continue

                print(f"[{s.node_id}] Recebido {msg.subtipo} de {remote_ip} (msg_id={msg.msg_id})")

                ack = AckPacket(orig_subtype=msg.subtipo, msg_id=msg.msg_id)
                try:
                    s.udp_sock.sendto(ack.serialize(), (remote_ip, UDP_PORT))
                    print(f"[{s.node_id}] ACK({msg.subtipo}) enviado para {remote_ip}")
                except OSError as e:
                    print(f"[{s.node_id}] erro ao enviar ACK({msg.subtipo}) para {remote_ip}: {e}")
                continue

            # ACK do JOIN
            if subtipo == ControlSubtype.ACK:
                try:
                    ack = AckPacket.deserialize(data)
                except Exception:
                    continue

                key = (remote_ip, ack.msg_id)
                with s._pending_lock:
                    entry = s._pending_control.pop(key, None)

                if entry is not None:
                    print(f"[{s.node_id}] ACK recebido de {remote_ip} para JOIN msg_id={ack.msg_id}")
                continue

            # ROUTE_WITHDRAW -> ACK
            if subtipo == ControlSubtype.ROUTE_WITHDRAW:
                try:
                    rw = RouteWithdrawPacket.deserialize(data)
                except Exception as e:
                    print(f"[{s.node_id}] ROUTE_WITHDRAW inválido de {remote_ip}: {e}")
                    continue

                print(f"[{s.node_id}] Recebido ROUTE_WITHDRAW de {remote_ip} para streams={rw.stream_ids}")

                ack = AckPacket(orig_subtype=ControlSubtype.ROUTE_WITHDRAW, msg_id=rw.msg_id)
                try:
                    s.udp_sock.sendto(ack.serialize(), (remote_ip, UDP_PORT))
                    print(f"[{s.node_id}] ACK(ROUTE_WITHDRAW) enviado para {remote_ip}")
                except OSError as e:
                    print(f"[{s.node_id}] erro ao enviar ACK(ROUTE_WITHDRAW) para {remote_ip}: {e}")
                continue

            # PING -> PONG
            if subtipo == ControlSubtype.PING:
                try:
                    ping = HeartbeatPing.deserialize(data)
                except Exception as e:
                    print(f"[{s.node_id}] PING inválido de {remote_ip}: {e}")
                    continue

                pong = HeartbeatPong(ping.ping_id)
                try:
                    s.udp_sock.sendto(pong.serialize(), (remote_ip, UDP_PORT))
                    print(f"[{s.node_id}] PONG enviado para {remote_ip} (ping_id={ping.ping_id})")
                except OSError as e:
                    print(f"[{s.node_id}] erro ao enviar PONG para {remote_ip}: {e}")
                continue

            # REQUEST (PLAY/PAUSE/TEARDOWN)
            if subtipo == ControlSubtype.REQUEST:
                try:
                    req = StreamRequestPacket.deserialize(data)
                except Exception as e:
                    print(f"[{s.node_id}] REQUEST inválido de {remote_ip}: {e}")
                    continue

                # ACK para reliability
                try:
                    ack = AckPacket(orig_subtype=ControlSubtype.REQUEST, msg_id=req.req_id)
                    s.udp_sock.sendto(ack.serialize(), (remote_ip, UDP_PORT))
                except OSError as e:
                    print(f"[{s.node_id}] Error sending ACK(REQUEST) to {remote_ip}: {e}")

                self._handle_stream_request(remote_ip, req)
                continue

            # NACK (retransmissão RTP)
            if subtipo == ControlSubtype.NACK:
                try:
                    nack = NackPacket.deserialize(data)
                except Exception as e:
                    print(f"[{s.node_id}] NACK inválido de {remote_ip}: {e}")
                    continue

                self._handle_nack(remote_ip, nack)
                continue

    def _handle_stream_request(self, remote_ip: str, req: StreamRequestPacket):
        s = self.s
        stream_id = req.stream_id
        method = req.method

        print(f"[{s.node_id}] REQUEST {method} from {remote_ip} for stream {stream_id}")

        # Check if stream exists
        if stream_id not in s.stream_ids:
            resp = StreamResponseMessage(req.req_id, 404, "Stream not found")
            try:
                s.udp_sock.sendto(resp.serialize(), (remote_ip, UDP_PORT))
            except OSError as e:
                print(f"[{s.node_id}] erro ao enviar RESPONSE para {remote_ip}: {e}")
            return

        # Ensure StreamSessionPacket exists
        if stream_id not in s.stream_sessions:
            video_path = os.path.join("server/streams", str(stream_id))
            ssrc = int(time.time() * 1000) & 0xFFFFFFFF
            s.stream_sessions[stream_id] = StreamSessionPacket(stream_id=stream_id, video_path=video_path, ssrc=ssrc)

        session = s.stream_sessions[stream_id]

        if method == RequestMethod.PLAY:
            with s._active_streams_lock:
                session.subscribers += 1

                if stream_id not in s._active_streams:
                    s._active_streams[stream_id] = set()

                s._active_streams[stream_id].add(remote_ip)
                session.running = True

                print(
                    f"[{s.node_id}] PLAY stream {stream_id} for {remote_ip} "
                    f"(subscribers: {session.subscribers}, IPs: {s._active_streams[stream_id]})"
                )

            resp = StreamResponseMessage(req.req_id, 0, "OK")

        elif method == RequestMethod.PAUSE:
            # manténs o teu "pass" (sem mudar lógica)
            resp = StreamResponseMessage(req.req_id, 0, "OK")

        elif method == RequestMethod.TEARDOWN:
            with s._active_streams_lock:
                if stream_id in s._active_streams:
                    s._active_streams[stream_id].discard(remote_ip)
                    print(
                        f"[{s.node_id}] TEARDOWN stream {stream_id} for {remote_ip} "
                        f"(remaining IPs: {s._active_streams[stream_id]})"
                    )

                    stream_key = (stream_id, remote_ip)
                    with s._stream_threads_lock:
                        if stream_key in s._stream_threads:
                            s._stream_threads[stream_key]["event"].set()

            resp = StreamResponseMessage(req.req_id, 0, "OK")
        else:
            resp = StreamResponseMessage(req.req_id, 400, "Unknown method")

        try:
            s.udp_sock.sendto(resp.serialize(), (remote_ip, UDP_PORT))
        except OSError as e:
            print(f"[{s.node_id}] erro ao enviar RESPONSE para {remote_ip}: {e}")

    def _handle_nack(self, remote_ip: str, nack: "NackPacket"):
        s = self.s
        key = (nack.stream_id, remote_ip)
        hist = s.rtx_history.get(key)

        if not hist:
            print(f"[{s.node_id}] Sem history para stream {nack.stream_id} -> {remote_ip}")
            return

        print(
            f"[{s.node_id}] NACK de {remote_ip} para stream={nack.stream_id} "
            f"seq=[{nack.first_seq},{nack.last_seq}]"
        )

        for seq in range(nack.first_seq, nack.last_seq + 1):
            pkt = hist["packets"].get(seq)
            if pkt:
                try:
                    s.udp_sock.sendto(pkt, (remote_ip, UDP_PORT))
                    print(f"[{s.node_id}] Retransmit seq={seq} stream={nack.stream_id} -> {remote_ip}")
                except OSError as e:
                    print(f"[{s.node_id}] erro ao retransmitir seq={seq} para {remote_ip}: {e}")
