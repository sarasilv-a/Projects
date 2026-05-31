import time
import threading
import random

from config import UDP_PORT
from protocols.neighbor_control_packet import JoinPacket, LeavePacket, NeighborControlPacket
from protocols.stream_request_packet import StreamRequestPacket, StreamResponseMessage, RequestMethod
from protocols.stream_list_packet import StreamListRequestPacket, StreamListResponsePacket
from protocols.ack_packet import AckPacket
from protocols.control_types import MessageType, ControlSubtype
from protocols.heartbeat_packet import HeartbeatPing, HeartbeatPong
from protocols.route_withdraw_packet import RouteWithdrawPacket


class ClientNetLoop:
    def __init__(self, client, stream_engine):
        self.client = client
        self.stream = stream_engine

    # ------------------------------------------------------------
    # JOIN / LEAVE
    # ------------------------------------------------------------
    def join_network(self):
        c = self.client
        if not c.neighbor_ip:
            print(f"[CLIENT {c.client_id}] sem vizinho configurado, não posso fazer JOIN.")
            c.connected = False
            return

        neighbor_ip = c.neighbor_ip
        max_retries = 5
        timeout = 10

        msg_id = random.randint(1, 2**32 - 1)
        join_msg = JoinPacket(msg_id).serialize()
        key = (neighbor_ip, msg_id)

        with c._pending_lock:
            c._pending_control[key] = {"retries": 0, "failed": False}

        def worker():
            while True:
                with c._pending_lock:
                    entry = c._pending_control.get(key)

                if entry is None:
                    return
                if entry.get("failed"):
                    return

                if entry["retries"] >= max_retries:
                    print(
                        f"[CLIENT {c.client_id}] vizinho {neighbor_ip} não respondeu ao JOIN "
                        f"após {max_retries} tentativas."
                    )
                    with c._pending_lock:
                        if key in c._pending_control:
                            c._pending_control[key]["failed"] = True
                    return

                attempt = entry["retries"] + 1
                print(
                    f"[CLIENT {c.client_id}] JOIN tentativa {attempt}/{max_retries} "
                    f"para {neighbor_ip}:{UDP_PORT}"
                )
                try:
                    c.udp_sock.sendto(join_msg, (neighbor_ip, UDP_PORT))
                except OSError as e:
                    print(
                        f"[CLIENT {c.client_id}] erro UDP ao enviar JOIN para "
                        f"{neighbor_ip}:{UDP_PORT}: {e}"
                    )

                with c._pending_lock:
                    if key in c._pending_control:
                        c._pending_control[key]["retries"] += 1

                time.sleep(timeout)

        threading.Thread(target=worker, daemon=True).start()

        total_wait = max_retries * (timeout + 0.1)
        start = time.time()
        success = False
        while time.time() - start < total_wait:
            with c._pending_lock:
                entry = c._pending_control.get(key)

            if entry is None:
                success = True
                break
            if entry.get("failed"):
                success = False
                break

            time.sleep(0.1)

        with c._pending_lock:
            c._pending_control.pop(key, None)

        if success:
            print(f"[CLIENT {c.client_id}] JOIN confirmado por {neighbor_ip}")
            c.connected = True
        else:
            print(f"[CLIENT {c.client_id}] JOIN falhou — vizinho não alcançável")
            c.connected = False

    def leave_network(self):
        c = self.client
        if not c.connected:
            print(f"[CLIENT {c.client_id}] not connected — skipping LEAVE")
            return

        msg_id = random.randint(1, 2**32 - 1)
        msg = LeavePacket(msg_id).serialize()
        try:
            c.udp_sock.sendto(msg, (c.neighbor_ip, UDP_PORT))
            print(
                f"[CLIENT {c.client_id}] LEAVE (UDP) enviado para "
                f"{c.neighbor_ip}:{UDP_PORT} msg_id={msg_id}"
            )
        except OSError as e:
            print(
                f"[CLIENT {c.client_id}] LEAVE (UDP) falhou para "
                f"{c.neighbor_ip}:{UDP_PORT}: {e}"
            )
        c.connected = False

    # ------------------------------------------------------------
    # Reliability helpers
    # ------------------------------------------------------------
    def _send_with_retries(self, payload: bytes, msg_id: int, orig_subtype: int, *,
                           target_ip: str = None, max_retries: int = 5, timeout: float = 0.5) -> bool:
        c = self.client
        dest_ip = target_ip or c.neighbor_ip
        if not dest_ip:
            return False

        key = (dest_ip, msg_id)
        with c._pending_lock:
            c._pending_control[key] = {"retries": 0, "failed": False, "orig_subtype": orig_subtype}

        def worker():
            while True:
                with c._pending_lock:
                    entry = c._pending_control.get(key)

                if entry is None or entry.get("failed"):
                    return

                if entry["retries"] >= max_retries:
                    print(
                        f"[CLIENT {c.client_id}] sem ACK para msg_id={msg_id} "
                        f"depois de {max_retries} tentativas."
                    )
                    with c._pending_lock:
                        if key in c._pending_control:
                            c._pending_control[key]["failed"] = True
                    return

                attempt = entry["retries"] + 1
                try:
                    c.udp_sock.sendto(payload, (dest_ip, UDP_PORT))
                except OSError as e:
                    print(
                        f"[CLIENT {c.client_id}] erro ao enviar (tentativa {attempt}) "
                        f"para {dest_ip}:{UDP_PORT}: {e}"
                    )

                with c._pending_lock:
                    if key in c._pending_control:
                        c._pending_control[key]["retries"] += 1

                time.sleep(timeout)

        threading.Thread(target=worker, daemon=True).start()

        deadline = time.time() + max_retries * (timeout + 0.05)
        while time.time() < deadline:
            with c._pending_lock:
                entry = c._pending_control.get(key)

            if entry is None:
                return True
            if entry.get("failed"):
                with c._pending_lock:
                    c._pending_control.pop(key, None)
                return False

            time.sleep(0.05)

        with c._pending_lock:
            c._pending_control.pop(key, None)
        return False

    def _wait_for_response(self, req_id: int, timeout_total: float = 2.0):
        c = self.client
        resp = None
        deadline = time.time() + timeout_total
        while time.time() < deadline:
            with c._requests_lock:
                entry = c.pending_requests.get(req_id)
                if entry and entry.get("response") is not None:
                    resp = entry["response"]
                    break
            time.sleep(0.05)
        return resp

    def _send_stream_request(self, stream_id: str, method: int):
        c = self.client
        req_id = int(time.time() * 1000) & 0xFFFFFFFF
        req = StreamRequestPacket(
            req_id=req_id,
            client_id=c.client_id,
            stream_id=stream_id,
            method=method,
        )

        payload = req.serialize()
        method_name = {
            RequestMethod.PLAY: "PLAY",
            RequestMethod.PAUSE: "PAUSE",
            RequestMethod.TEARDOWN: "TEARDOWN",
            RequestMethod.SETUP: "SETUP",
        }.get(method, str(method))

        print(
            f"[CLIENT {c.client_id}] a enviar REQUEST {method_name} (req_id={req_id}) "
            f"para {c.neighbor_ip}:{UDP_PORT} (stream_id={stream_id}) via UDP"
        )

        with c._requests_lock:
            c.pending_requests[req_id] = {"response": None}

        ack_ok = self._send_with_retries(payload, req_id, ControlSubtype.REQUEST)

        resp = None
        if ack_ok:
            resp = self._wait_for_response(req_id)

        with c._requests_lock:
            c.pending_requests.pop(req_id, None)

        if not ack_ok:
            print(
                f"[CLIENT {c.client_id}] REQUEST {method_name} não confirmado por ACK "
                f"(req_id={req_id})."
            )

        return ack_ok, resp

    # ------------------------------------------------------------
    # Stream list request
    # ------------------------------------------------------------
    def request_stream_list(self):
        c = self.client

        req_id = int(time.time() * 1000) & 0xFFFFFFFF
        req = StreamListRequestPacket(req_id=req_id, client_id=c.client_id)
        payload = req.serialize()

        print(
            f"[CLIENT {c.client_id}] a enviar STREAM_LIST_REQUEST (req_id={req_id}) "
            f"para {c.neighbor_ip}:{UDP_PORT} via UDP"
        )

        with c._requests_lock:
            c.pending_requests[req_id] = {"response": None}

        try:
            c.udp_sock.sendto(payload, (c.neighbor_ip, UDP_PORT))
        except OSError as e:
            print(
                f"[CLIENT {c.client_id}] erro ao enviar STREAM_LIST_REQUEST UDP para "
                f"{c.neighbor_ip}:{UDP_PORT}: {e}"
            )
            with c._requests_lock:
                c.pending_requests.pop(req_id, None)
            return

        resp = None
        timeout_total = 2.0
        deadline = time.time() + timeout_total
        while time.time() < deadline:
            with c._requests_lock:
                entry = c.pending_requests.get(req_id)
                if entry and entry["response"] is not None:
                    resp = entry["response"]
                    break
            time.sleep(0.05)

        with c._requests_lock:
            c.pending_requests.pop(req_id, None)

        if resp is None:
            print("[CLIENT] não recebeu resposta à STREAM_LIST_REQUEST.\n")
            return

        print("\n=== Streams disponíveis no nó vizinho ===")
        if not resp.entries:
            print("(nenhuma stream anunciada)")
        else:
            for stream_id, server_id in resp.entries:
                print(f"- stream_id = {stream_id}  (server = {server_id})")
        print("=========================================\n")

    # ------------------------------------------------------------
    # UDP loop
    # ------------------------------------------------------------
    def udp_loop(self):
        c = self.client
        while True:
            try:
                data, addr = c.udp_sock.recvfrom(65535)
                remote_ip, remote_port = addr
            except OSError as e:
                print(f"[CLIENT {c.client_id}] erro em udp_loop recv: {e}")
                time.sleep(0.1)
                continue

            tipo = data[0]

            # STREAM
            if tipo == MessageType.STREAM:
                self.stream.handle_stream_packet(data, remote_ip)
                continue

            # CONTROL
            if tipo != MessageType.CONTROL:
                continue
            if len(data) < 2:
                continue
            subtipo = data[1]

            if subtipo == ControlSubtype.ACK:
                try:
                    ack = AckPacket.deserialize(data)
                except Exception as e:
                    print(f"[CLIENT {c.client_id}] ACK inválido de {remote_ip}: {e}")
                    continue

                key = (remote_ip, ack.msg_id)
                with c._pending_lock:
                    entry = c._pending_control.pop(key, None)

                if entry is not None:
                    print(
                        f"[CLIENT {c.client_id}] ACK recebido de {remote_ip} "
                        f"para msg_id={ack.msg_id} (orig_subtype={ack.orig_subtype})"
                    )

            elif subtipo == ControlSubtype.PING:
                try:
                    ping = HeartbeatPing.deserialize(data)
                except Exception as e:
                    print(f"[CLIENT {c.client_id}] PING inválido de {remote_ip}: {e}")
                    continue

                pong = HeartbeatPong(ping.ping_id)
                try:
                    c.udp_sock.sendto(pong.serialize(), (remote_ip, UDP_PORT))
                except OSError as e:
                    print(f"[CLIENT {c.client_id}] erro ao enviar PONG para {remote_ip}: {e}")

            elif subtipo == ControlSubtype.PONG:
                print(f"[CLIENT {c.client_id}] PONG recebido de {remote_ip} (ignorando por agora)")

            elif subtipo == ControlSubtype.RESPONSE:
                try:
                    resp = StreamResponseMessage.deserialize(data)
                except Exception as e:
                    print(f"[CLIENT {c.client_id}] RESPONSE UDP inválida de {remote_ip}: {e}")
                    continue

                with c._requests_lock:
                    entry = c.pending_requests.get(resp.req_id)
                    if entry is not None:
                        entry["response"] = resp
                with c._pending_lock:
                    c._pending_control.pop((remote_ip, resp.req_id), None)

            elif subtipo == ControlSubtype.STREAM_LIST_RESPONSE:
                try:
                    list_resp = StreamListResponsePacket.deserialize(data)
                except Exception as e:
                    print(f"[CLIENT {c.client_id}] STREAM_LIST_RESPONSE inválida de {remote_ip}: {e}")
                    continue

                with c._requests_lock:
                    entry = c.pending_requests.get(list_resp.req_id)
                    if entry is not None:
                        entry["response"] = list_resp

            elif subtipo in (ControlSubtype.JOIN, ControlSubtype.LEAVE):
                try:
                    neigh_msg = NeighborControlPacket.deserialize(data)
                except Exception as e:
                    print(f"[CLIENT {c.client_id}] JOIN/LEAVE inválido de {remote_ip}: {e}")
                    continue

                if neigh_msg.subtipo == ControlSubtype.LEAVE:
                    print(f"[CLIENT {c.client_id}] Nodo {remote_ip} vai sair da rede.")

                    if remote_ip in c.neighbors:
                        try:
                            c.neighbors.remove(remote_ip)
                            print(f"[CLIENT {c.client_id}] Vizinho {remote_ip} removido da lista de neighbors.")
                        except ValueError:
                            pass

                    if c.neighbor_ip == remote_ip:
                        c.neighbor_ip = None

                    ack = AckPacket(orig_subtype=ControlSubtype.LEAVE, msg_id=neigh_msg.msg_id)
                    try:
                        c.udp_sock.sendto(ack.serialize(), (remote_ip, UDP_PORT))
                        print(f"[CLIENT {c.client_id}] ACK(LEAVE) enviado para {remote_ip}")
                    except OSError as e:
                        print(f"[CLIENT {c.client_id}] erro ao enviar ACK(LEAVE) para {remote_ip}: {e}")

                    c._request_new_connection(remote_ip)

            elif subtipo == ControlSubtype.ROUTE_WITHDRAW:
                try:
                    rw = RouteWithdrawPacket.deserialize(data)
                except Exception as e:
                    print(f"[CLIENT {c.client_id}] Invalid ROUTE_WITHDRAW from {remote_ip}: {e}")
                    continue

                ack = AckPacket(orig_subtype=ControlSubtype.ROUTE_WITHDRAW, msg_id=rw.msg_id)
                try:
                    c.udp_sock.sendto(ack.serialize(), (remote_ip, UDP_PORT))
                    print(f"[CLIENT {c.client_id}] ACK(ROUTE_WITHDRAW) enviado para {remote_ip}")
                except OSError as e:
                    print(f"[CLIENT {c.client_id}] erro ao enviar ACK(ROUTE_WITHDRAW) para {remote_ip}: {e}")
