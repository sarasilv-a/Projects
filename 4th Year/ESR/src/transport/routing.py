import time
import random
import threading
from collections import deque
from typing import TYPE_CHECKING

from config import UDP_PORT
from protocols.flooding_packet import FloodingPacket
from protocols.route_withdraw_packet import RouteWithdrawPacket
from protocols.ack_packet import AckPacket
from protocols.control_types import MessageType, ControlSubtype


if TYPE_CHECKING:
    from transport.node import Node

class RoutingManager:
    def __init__(self, node: "Node"):
        self.node = node

    # ---------------- ACK genérico de controlo ----------------

    # ---------------- ANNOUNCE ----------------
    def handle_announce(self, remote_ip: str, msg: FloodingPacket):
        now = time.time()

        with self.node._lock:
            ignore_until = self.node.dead_cooldown.get(remote_ip)

        if ignore_until is not None:
            if now < ignore_until:
                print(
                    f"[{self.node.node_id}] Ignoring ANNOUNCE from {remote_ip} "
                    f"(dead cooldown active)"
                )
                return
            else:
                with self.node._lock:
                    self.node.dead_cooldown.pop(remote_ip, None)

        filtered_sids = []
        with self.node._lock:
            for sid in msg.stream_ids:
                key = (remote_ip, sid)
                w_until = self.node.recent_withdraws.get(key)
                if w_until is not None:
                    if now < w_until:
                        continue
                    else:
                        self.node.recent_withdraws.pop(key, None)
                filtered_sids.append(sid)

        if not filtered_sids:
            print(
                f"[{self.node.node_id}] ANNOUNCE from {remote_ip} ignored "
                f"(all streams in withdraw cooldown)"
            )
            return

        hop_delay_ms = max(0.0, (now - msg.ts_sent) * 1000.0)

        flow_id = msg.flow_id
        flow_key = (remote_ip, flow_id)

        with self.node._flows_lock:
            st = self.node.flow_state.get(flow_key)
            if st is None:
                st = {
                    "from_ip": remote_ip,
                    "base_rtt_ms": msg.rtt_ms,
                    "base_loss_pct": msg.loss_pct,
                    "stream_ids": list(filtered_sids),
                    "received": 0,
                    "min_delay_ms": hop_delay_ms,
                    "first_time": now,
                }
                self.node.flow_state[flow_key] = st
            else:
                st["min_delay_ms"] = min(st["min_delay_ms"], hop_delay_ms)

            st["received"] += 1
            received_now = st["received"]

        if received_now >= self.node.FLOW_EXPECTED_PER_BURST:
            self._finalize_flow_and_reflood(remote_ip, flow_id)

    # ---------------- ROUTE_WITHDRAW ----------------
    def handle_route_withdraw(self, remote_ip: str, rw: RouteWithdrawPacket):
        to_propagate = []
        now = time.time()
        lost_sids = []

        with self.node._lock:
            for sid in rw.stream_ids:
                info = self.node.routing_table.get(sid)
                if info is not None and info.get("next_hop") == remote_ip:
                    self.node.routing_table.pop(sid, None)
                    to_propagate.append(sid)
                    lost_sids.append(sid)

            if lost_sids:
                for flow_id, fmap in list(self.node.neighbor_history.items()):
                    fmap.pop(remote_ip, None)
                    if not fmap:
                        self.node.neighbor_history.pop(flow_id, None)

            # cooldown para qualquer announce deste vizinho para estes streams
            timeout = self.node.heartbeat.ping_timeout(
                remote_ip, factor=1.0, default_ms=1000.0
            )
            if timeout <= 0:
                timeout = 1.0
            for sid in rw.stream_ids:
                key = (remote_ip, sid)
                self.node.recent_withdraws[key] = now + timeout

        ack = AckPacket(orig_subtype=ControlSubtype.ROUTE_WITHDRAW, msg_id=rw.msg_id)
        try:
            self.node.udp_sock.sendto(ack.serialize(), (remote_ip, UDP_PORT))
        except OSError as e:
            print(
                f"[{self.node.node_id}] Error sending ACK(ROUTE_WITHDRAW) to {remote_ip}: {e}"
            )

        if to_propagate:
            print(
                f"[{self.node.node_id}] ROUTE_WITHDRAW from {remote_ip} "
                f"removed streams={to_propagate} – propagating"
            )
            self.propagate_route_withdraw(to_propagate, origin_ip=remote_ip)
        else:
            print(
                f"[{self.node.node_id}] ROUTE_WITHDRAW from {remote_ip} "
                f"for streams={rw.stream_ids} (no active routes to drop)"
            )

    # ---------------- COST / ROUTING TABLE ----------------
    def _compute_cost(self, rtt_ms: float, loss_pct: float) -> float:
        return 0.5 * rtt_ms + 0.5 * loss_pct

    def _update_routing_from_announce(
        self,
        remote_ip: str,
        msg: FloodingPacket,
        new_rtt_ms: float,
        new_loss_pct: float,
        neighbor_costs: dict,
    ):
        server_id = msg.flow_id.split(":", 1)[0]
        new_cost = self._compute_cost(new_rtt_ms, new_loss_pct)
        IMPROVE_PCT = 0.50 # 50 %

        for sid in msg.stream_ids:
            current = self.node.routing_table.get(sid)
            if current is None:
                self.node.routing_table[sid] = {
                    "server_id": server_id,
                    "next_hop": remote_ip,
                    "rtt_ms": new_rtt_ms,
                    "loss_pct": new_loss_pct,
                    "cost": new_cost,
                }
                print(
                    f"[{self.node.node_id}] ROUTE NEW stream={sid} via {remote_ip} "
                    f"server={server_id} rtt={new_rtt_ms:.2f}ms "
                    f"loss={new_loss_pct:.2f}% cost={new_cost:.2f}"
                )
            else:
                old_next = current["next_hop"]
                old_rtt = current["rtt_ms"]
                old_loss = current["loss_pct"]
                old_cost = current["cost"]

                if remote_ip == old_next:
                    current["rtt_ms"] = new_rtt_ms
                    current["loss_pct"] = new_loss_pct
                    current["cost"] = new_cost
                else:
                    current_cost_old_next = old_cost
                    if neighbor_costs is not None:
                        metrics_old = neighbor_costs.get(old_next)
                        if metrics_old is not None:
                            current_cost_old_next = metrics_old["cost"]
                        else:
                            # current_cost_old_next = float("inf")
                            # não há métricas deste flow para o old_next -> usa o custo atual guardado
                            current_cost_old_next = old_cost

                    if new_cost <= current_cost_old_next * (1.0 - IMPROVE_PCT):
                        self.node.routing_table[sid] = {
                            "server_id": server_id,
                            "next_hop": remote_ip,
                            "rtt_ms": new_rtt_ms,
                            "loss_pct": new_loss_pct,
                            "cost": new_cost,
                        }
                        print(
                            f"[{self.node.node_id}] ROUTE SWITCH stream={sid} "
                            f"{old_next} -> {remote_ip} server={server_id} "
                            f"rtt {old_rtt:.2f}->{new_rtt_ms:.2f}ms "
                            f"loss {old_loss:.2f}->{new_loss_pct:.2f}% "
                            f"cost {current_cost_old_next:.2f}->{new_cost:.2f}"
                        )

    def _finalize_flow_and_reflood(self, from_ip: str, flow_id: str):
        flow_key = (from_ip, flow_id)
        with self.node._flows_lock:
            st = self.node.flow_state.pop(flow_key, None)

        if st is None:
            return

        expected = self.node.FLOW_EXPECTED_PER_BURST
        received = st["received"]
        base_rtt_ms = st["base_rtt_ms"]
        base_loss_pct = st["base_loss_pct"]
        min_delay_ms = st["min_delay_ms"]
        stream_ids = st["stream_ids"]

        lost = max(0, expected - received)
        local_loss_pct = 100.0 * (float(lost) / float(expected))
        local_rtt_ms = min_delay_ms

        new_rtt_ms = base_rtt_ms + local_rtt_ms
        new_loss_pct = base_loss_pct + local_loss_pct

        flow_hist = self.node.neighbor_history.setdefault(flow_id, {})
        hist = flow_hist.get(from_ip)
        if hist is None:
            hist = deque(maxlen=3)
            flow_hist[from_ip] = hist
        hist.append({"rtt_ms": new_rtt_ms, "loss_pct": new_loss_pct})

        avg_per_neighbor = {}
        for neigh_ip, h in flow_hist.items():
            if not h:
                continue
            sum_rtt = sum(m["rtt_ms"] for m in h)
            sum_loss = sum(m["loss_pct"] for m in h)
            avg_rtt_ms = sum_rtt / len(h)
            avg_loss_pct = sum_loss / len(h)
            avg_cost = self._compute_cost(avg_rtt_ms, avg_loss_pct)
            avg_per_neighbor[neigh_ip] = {
                "rtt_ms": avg_rtt_ms,
                "loss_pct": avg_loss_pct,
                "cost": avg_cost,
            }

        if not avg_per_neighbor:
            return

        best_ip = min(
            avg_per_neighbor.keys(),
            key=lambda ip: avg_per_neighbor[ip]["cost"],
        )
        best_metrics = avg_per_neighbor[best_ip]
        best_avg_rtt = best_metrics["rtt_ms"]
        best_avg_loss = best_metrics["loss_pct"]
        best_avg_cost = best_metrics["cost"]

        summary_msg = FloodingPacket(
            flow_id=flow_id,
            seq=0,
            ts_sent=time.time(),
            rtt_ms=best_avg_rtt,
            loss_pct=best_avg_loss,
            stream_ids=stream_ids,
        )

        self._update_routing_from_announce(
            best_ip,
            summary_msg,
            best_avg_rtt,
            best_avg_loss,
            avg_per_neighbor,
        )

        FLOOD_EPS = 0.10

        last = self.node.best_flow_metric.get(flow_id)
        if last is not None:
            old_cost = last["cost"]
            if old_cost * (1.0 - FLOOD_EPS) <= best_avg_cost <= old_cost * (
                1.0 + FLOOD_EPS
            ):
                return

        self.node.best_flow_metric[flow_id] = {
            "rtt_ms": best_avg_rtt,
            "loss_pct": best_avg_loss,
            "cost": best_avg_cost,
        }

        ts_now = time.time()
        for neighbor_ip in self.node.neighbors:
            if neighbor_ip == from_ip:
                continue
            if neighbor_ip == best_ip:
                continue

            with self.node._lock:
                filtered_sids = []
                for sid in stream_ids:
                    info = self.node.routing_table.get(sid)
                    if (
                        info is not None
                        and info.get("next_hop") == neighbor_ip
                    ):
                        continue
                    filtered_sids.append(sid)

            if not filtered_sids:
                continue

            for seq in range(1, expected + 1):
                msg = FloodingPacket(
                    flow_id=flow_id,
                    seq=seq,
                    ts_sent=ts_now,
                    rtt_ms=best_avg_rtt,
                    loss_pct=best_avg_loss,
                    stream_ids=stream_ids,
                )
                try:
                    self.node.udp_sock.sendto(msg.serialize(), (neighbor_ip, UDP_PORT))
                except OSError as e:
                    print(
                        f"[{self.node.node_id}] UDP send error to {neighbor_ip}:{UDP_PORT}: {e}"
                    )

    def _check_expired_flows(self):
        now = time.time()
        to_finalize = []

        with self.node._flows_lock:
            for (from_ip, flow_id), st in list(self.node.flow_state.items()):
                first_time = st.get("first_time")
                received = st.get("received", 0)

                if first_time is None or received <= 0:
                    continue

                if (now - first_time) >= self.node.FLOW_BURST_TIMEOUT:
                    to_finalize.append((from_ip, flow_id))

        for from_ip, flow_id in to_finalize:
            self._finalize_flow_and_reflood(from_ip, flow_id)

    def flow_cleanup_loop(self):
        while True:
            self._check_expired_flows()
            time.sleep(0.1)

    # ---------------- ROUTE_WITHDRAW PROPAGATION ----------------
    def propagate_route_withdraw(self, stream_ids, origin_ip: str):
        if not stream_ids:
            return

        with self.node._lock:
            neighbors = [n for n in self.node.neighbors if n != origin_ip]

        if not neighbors:
            return

        max_retries = 5

        for nb in neighbors:
            msg_id = random.randint(1, 2**32 - 1)
            msg = RouteWithdrawPacket(msg_id, stream_ids)
            data = msg.serialize()
            key = (nb, msg_id)

            with self.node._pending_lock:
                self.node._pending_control[key] = {"retries": 0}

            def worker(ip, key, data):
                while True:
                    with self.node._pending_lock:
                        entry = self.node._pending_control.get(key)

                    if entry is None:
                        return

                    if entry["retries"] >= max_retries:
                        print(
                            f"[{self.node.node_id}] {ip} did not ACK ROUTE_WITHDRAW"
                        )
                        with self.node._pending_lock:
                            self.node._pending_control.pop(key, None)
                        return

                    attempt = entry["retries"] + 1
                    print(
                        f"[{self.node.node_id}] ROUTE_WITHDRAW to {ip} "
                        f"(attempt {attempt}/{max_retries}, streams={stream_ids})"
                    )

                    try:
                        self.node.udp_sock.sendto(data, (ip, UDP_PORT))
                    except OSError as e:
                        print(
                            f"[{self.node.node_id}] UDP error sending "
                            f"ROUTE_WITHDRAW to {ip}: {e}"
                        )

                    with self.node._pending_lock:
                        if key in self.node._pending_control:
                            self.node._pending_control[key]["retries"] += 1

                    timeout = self.node.heartbeat.ping_timeout(
                        ip, factor=1.0, default_ms=1000.0
                    )
                    time.sleep(timeout)

            threading.Thread(
                target=worker,
                args=(nb, key, data),
                daemon=True,
            ).start()
