import time
import threading
import random

from config import UDP_PORT
from protocols.neighbor_control_packet import JoinPacket
from protocols.flooding_packet import FloodingPacket


class ServerControl:
    def __init__(self, server):
        self.s = server

    def send_join_to_neighbors(self):
        s = self.s
        for neighbor_ip in list(s.neighbors):
            msg_id = random.randint(1, 2**32 - 1)
            join_msg = JoinPacket(msg_id).serialize()
            key = (neighbor_ip, msg_id)

            with s._pending_lock:
                s._pending_control[key] = {"retries": 0}

            def worker(ip, msg_id, join_msg, key):
                max_retries = 5
                timeout = 1.0

                while True:
                    with s._pending_lock:
                        entry = s._pending_control.get(key)

                    if entry is None:
                        print(f"[{s.node_id}] JOIN confirmado por {ip}")
                        return

                    if entry["retries"] >= max_retries:
                        print(f"[{s.node_id}] {ip} NÃO respondeu ao JOIN — removido")
                        with s._pending_lock:
                            s._pending_control.pop(key, None)
                        if ip in s.neighbors:
                            s.neighbors.remove(ip)
                        return

                    attempt = entry["retries"] + 1
                    print(f"[{s.node_id}] JOIN tentativa {attempt}/{max_retries} para {ip}")

                    try:
                        s.udp_sock.sendto(join_msg, (ip, UDP_PORT))
                    except OSError as e:
                        print(f"[{s.node_id}] erro UDP ao enviar JOIN para {ip}: {e}")

                    with s._pending_lock:
                        if key in s._pending_control:
                            s._pending_control[key]["retries"] += 1

                    time.sleep(timeout)

            threading.Thread(
                target=worker,
                args=(neighbor_ip, msg_id, join_msg, key),
                daemon=True,
            ).start()

    def server_flood_loop(self):
        s = self.s
        time.sleep(5)
        FLOW_PACKETS_PER_BURST = 5
        BURST_INTERVAL = 10

        server_id = s.node_id
        burst_id = 0

        while True:
            burst_id += 1
            flow_id = f"{server_id}:{burst_id}"
            ts_now = time.time()

            print(f"[{s.node_id}] Flood burst {burst_id} (flow_id={flow_id}) to neighbors: {s.neighbors}")

            for neighbor_ip in s.neighbors:
                for _ in range(FLOW_PACKETS_PER_BURST):
                    s._global_seq += 1
                    seq = s._global_seq

                    msg = FloodingPacket(
                        flow_id=flow_id,
                        seq=seq,
                        ts_sent=ts_now,
                        rtt_ms=0.0,
                        loss_pct=0.0,
                        stream_ids=s.stream_ids,
                    )

                    print(
                        f"[{s.node_id}] ANNOUNCE -> {neighbor_ip}:{UDP_PORT} "
                        f"flow_id = {flow_id} seq = {seq}"
                    )

                    s.udp_sock.sendto(msg.serialize(), (neighbor_ip, UDP_PORT))

            time.sleep(BURST_INTERVAL)
