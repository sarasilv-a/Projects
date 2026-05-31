import time
import threading
from typing import TYPE_CHECKING

from config import UDP_PORT


if TYPE_CHECKING:
    from transport.node import Node


class ReliableControlManager:
    def __init__(self, node: "Node"):
        self.node = node

    def handle_ack(self, remote_ip: str, ack):
        key = (remote_ip, ack.msg_id)
        with self.node._pending_lock:
            entry = self.node._pending_control.pop(key, None)

        if entry is not None:
            print(
                f"[{self.node.node_id}] ACK from {remote_ip} "
                f"(subtype={ack.orig_subtype}, msg_id={ack.msg_id})"
            )

    def send_with_retries(
        self,
        payload: bytes,
        msg_id: int,
        dest_ip: str,
        orig_subtype: int,
        max_retries: int = 5,
        timeout: float = None,
    ) -> bool:
        if not dest_ip:
            return False

        key = (dest_ip, msg_id)
        with self.node._pending_lock:
            self.node._pending_control[key] = {
                "retries": 0,
                "failed": False,
                "orig_subtype": orig_subtype,
            }

        if timeout is not None:
            per_neighbor_timeout = timeout
        else:
            per_neighbor_timeout = self.node.heartbeat.ping_timeout(
                dest_ip, factor=1.0, default_ms=1000.0
            )
            per_neighbor_timeout = max(0.1, min(1.0, per_neighbor_timeout))

        def worker():
            while True:
                with self.node._pending_lock:
                    entry = self.node._pending_control.get(key)

                if entry is None or entry.get("failed"):
                    return

                if entry["retries"] >= max_retries:
                    print(
                        f"[{self.node.node_id}] no ACK for msg_id={msg_id} "
                        f"after {max_retries} attempts to {dest_ip}"
                    )
                    with self.node._pending_lock:
                        if key in self.node._pending_control:
                            self.node._pending_control[key]["failed"] = True
                    return

                attempt = entry["retries"] + 1
                try:
                    self.node.udp_sock.sendto(payload, (dest_ip, UDP_PORT))
                except OSError as e:
                    print(
                        f"[{self.node.node_id}] error sending (attempt {attempt}) "
                        f"to {dest_ip}:{UDP_PORT}: {e}"
                    )

                with self.node._pending_lock:
                    if key in self.node._pending_control:
                        self.node._pending_control[key]["retries"] += 1

                time.sleep(per_neighbor_timeout)

        threading.Thread(target=worker, daemon=True).start()

        deadline = time.time() + max_retries * (per_neighbor_timeout + 0.05)
        while time.time() < deadline:
            with self.node._pending_lock:
                entry = self.node._pending_control.get(key)

            if entry is None:
                return True
            if entry.get("failed"):
                with self.node._pending_lock:
                    self.node._pending_control.pop(key, None)
                return False

            time.sleep(0.05)

        with self.node._pending_lock:
            self.node._pending_control.pop(key, None)
        return False
