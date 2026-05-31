# tests/routing/test_routing.py
import time
import threading

import pytest

from config import UDP_PORT
from protocols.flooding_packet import FloodingPacket
from protocols.route_withdraw_packet import RouteWithdrawPacket
from protocols.ack_packet import AckPacket
from transport.routing import RoutingManager


# -------------------------------------------------------------------
# DUMMIES / STUBS
# -------------------------------------------------------------------

class DummySocket:
    def __init__(self):
        self.sent = []  # lista de (data, addr)

    def sendto(self, data: bytes, addr):
        self.sent.append((data, addr))


class DummyHeartbeat:
    def ping_timeout(self, ip: str, factor: float = 1.0, default_ms: float = 1000.0):
        # devolve timeout em segundos (ms -> s)
        return (default_ms * factor) / 1000.0


class FakeNode:
    """
    Node minimal para testar RoutingManager: só tem os atributos
    que o routing precisa.
    """
    def __init__(self, node_id="TestNode"):
        self.node_id = node_id

        # locks
        self._lock = threading.Lock()
        self._flows_lock = threading.Lock()
        self._pending_lock = threading.Lock()

        # estado de rede
        self.neighbors = []
        self.udp_sock = DummySocket()

        # estado de routing / flows
        self.dead_cooldown = {}         # ip -> ignore_until
        self.recent_withdraws = {}      # (ip, sid) -> ignore_until
        self.flow_state = {}            # (from_ip, flow_id) -> {...}
        self.FLOW_EXPECTED_PER_BURST = 3
        self.FLOW_BURST_TIMEOUT = 0.2   # mais pequeno para testes
        self.routing_table = {}         # sid -> {next_hop, server_id, ...}
        self.neighbor_history = {}      # flow_id -> {ip -> deque([...])}
        self.best_flow_metric = {}      # flow_id -> {rtt_ms, loss_pct, cost}

        # pending control (para ROUTE_WITHDRAW)
        self._pending_control = {}

        # heartbeat dummy (para ping_timeout)
        self.heartbeat = DummyHeartbeat()


# -------------------------------------------------------------------
# TESTES: handle_announce
# -------------------------------------------------------------------

def test_handle_announce_creates_flow_state_and_routing():
    node = FakeNode()
    routing = RoutingManager(node)

    remote_ip = "10.0.0.2"
    node.neighbors.append(remote_ip)

    flow_id = "server1:burst42"
    stream_ids = ["S1"]
    base_rtt_ms = 10.0
    base_loss_pct = 1.0

    # enviamos EXACTAMENTE FLOW_EXPECTED_PER_BURST announces
    for seq in range(1, node.FLOW_EXPECTED_PER_BURST + 1):
        msg = FloodingPacket(
            flow_id=flow_id,
            seq=seq,
            ts_sent=time.time(),
            rtt_ms=base_rtt_ms,
            loss_pct=base_loss_pct,
            stream_ids=stream_ids,
        )
        routing.handle_announce(remote_ip, msg)

    # depois do último pacote, o burst deve ter sido fechado
    flow_key = (remote_ip, flow_id)
    with node._flows_lock:
        assert flow_key not in node.flow_state

    # neighbor_history deve ter pelo menos uma entrada para este flow_id/from_ip
    assert flow_id in node.neighbor_history
    assert remote_ip in node.neighbor_history[flow_id]
    hist = node.neighbor_history[flow_id][remote_ip]
    assert len(hist) >= 1

    # routing_table deve agora ter rota para S1 via remote_ip
    assert "S1" in node.routing_table
    rt = node.routing_table["S1"]
    assert rt["next_hop"] == remote_ip
    assert rt["server_id"] == "server1"
    assert "cost" in rt


def test_handle_announce_respects_recent_withdraws():
    node = FakeNode()
    routing = RoutingManager(node)

    remote_ip = "10.0.0.2"
    sid = "S1"
    flow_id = "server1:burst43"

    # marcar que temos um withdraw recente deste vizinho para esta stream
    node.recent_withdraws[(remote_ip, sid)] = time.time() + 5.0

    msg = FloodingPacket(
        flow_id=flow_id,
        seq=1,
        ts_sent=time.time(),
        rtt_ms=10.0,
        loss_pct=0.0,
        stream_ids=[sid],
    )

    routing.handle_announce(remote_ip, msg)

    # não deve criar flow_state nem routing para esta stream
    assert (remote_ip, flow_id) not in node.flow_state
    assert sid not in node.routing_table


# -------------------------------------------------------------------
# TESTES: handle_route_withdraw
# -------------------------------------------------------------------

def test_handle_route_withdraw_removes_routes_and_sets_cooldown(monkeypatch):
    node = FakeNode()
    routing = RoutingManager(node)
    node.routing = routing  # para ser consistente com o Node real

    remote_ip = "10.0.0.2"
    node.neighbors.append("10.0.0.3")  # outro vizinho só para cenário

    # rota ativa para S1 via remote_ip
    node.routing_table["S1"] = {
        "server_id": "server1",
        "next_hop": remote_ip,
        "rtt_ms": 10.0,
        "loss_pct": 0.5,
        "cost": 20.0,
    }

    # neighbor_history com uma entrada qualquer
    from collections import deque
    node.neighbor_history["flowX"] = {
        remote_ip: deque([{"rtt_ms": 10.0, "loss_pct": 1.0}], maxlen=3),
        "other": deque([{"rtt_ms": 50.0, "loss_pct": 10.0}], maxlen=3),
    }

    called = {}

    def fake_propagate(stream_ids, origin_ip):
        called["streams"] = tuple(stream_ids)
        called["origin"] = origin_ip

    # evitar threads e side effects de verdade
    monkeypatch.setattr(routing, "propagate_route_withdraw", fake_propagate)

    rw = RouteWithdrawPacket(msg_id=999, stream_ids=["S1"])
    routing.handle_route_withdraw(remote_ip, rw)

    # rota S1 deve ser removida
    assert "S1" not in node.routing_table

    # neighbor_history deve ter removido o remote_ip deste flow
    assert "flowX" in node.neighbor_history
    assert remote_ip not in node.neighbor_history["flowX"]
    # mas "other" continua
    assert "other" in node.neighbor_history["flowX"]

    # recent_withdraws deve ter cooldown para (remote_ip, "S1")
    key = (remote_ip, "S1")
    assert key in node.recent_withdraws
    assert node.recent_withdraws[key] > time.time()

    # Foi enviado um ACK de ROUTE_WITHDRAW para remote_ip
    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    assert addr == (remote_ip, UDP_PORT)
    ack = AckPacket.deserialize(data)
    assert ack.msg_id == rw.msg_id

    # E a propagação foi chamada
    assert called["origin"] == remote_ip
    assert "S1" in called["streams"]


def test_handle_route_withdraw_no_active_routes(monkeypatch):
    node = FakeNode()
    routing = RoutingManager(node)
    node.routing = routing

    remote_ip = "10.0.0.2"

    called = {"count": 0}

    def fake_propagate(stream_ids, origin_ip):
        called["count"] += 1

    monkeypatch.setattr(routing, "propagate_route_withdraw", fake_propagate)

    # não há nenhuma rota com next_hop remote_ip
    node.routing_table["S1"] = {"next_hop": "10.0.0.99"}

    rw = RouteWithdrawPacket(msg_id=123, stream_ids=["S1"])
    routing.handle_route_withdraw(remote_ip, rw)

    # a rota S1 não é apagada (porque não usava este vizinho)
    assert "S1" in node.routing_table

    # não deve chamar propagate_route_withdraw
    assert called["count"] == 0

    # mas ainda assim deve enviar ACK
    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    assert addr == (remote_ip, UDP_PORT)
    ack = AckPacket.deserialize(data)
    assert ack.msg_id == rw.msg_id


# -------------------------------------------------------------------
# TESTES: _update_routing_from_announce (com histerese)
# -------------------------------------------------------------------

def test_update_routing_new_route_created():
    node = FakeNode()
    routing = RoutingManager(node)

    remote_ip = "10.0.0.2"
    flow_id = "serverX:burst1"
    msg = FloodingPacket(
        flow_id=flow_id,
        seq=0,
        ts_sent=time.time(),
        rtt_ms=10.0,
        loss_pct=0.0,
        stream_ids=["S1"],
    )

    neighbor_costs = {remote_ip: {"cost": routing._compute_cost(10.0, 0.0)}}

    routing._update_routing_from_announce(
        remote_ip=remote_ip,
        msg=msg,
        new_rtt_ms=10.0,
        new_loss_pct=0.0,
        neighbor_costs=neighbor_costs,
    )

    assert "S1" in node.routing_table
    rt = node.routing_table["S1"]
    assert rt["next_hop"] == remote_ip
    assert rt["server_id"] == "serverX"
    assert rt["rtt_ms"] == 10.0
    assert rt["loss_pct"] == 0.0


def test_update_routing_switch_only_if_better_cost():
    node = FakeNode()
    routing = RoutingManager(node)

    # rota atual via A
    node.routing_table["S1"] = {
        "server_id": "serverX",
        "next_hop": "A",
        "rtt_ms": 100.0,
        "loss_pct": 0.0,
        "cost": routing._compute_cost(100.0, 0.0),
    }

    neighbor_costs = {
        "A": {"cost": routing._compute_cost(100.0, 0.0)},
        "B": {"cost": routing._compute_cost(80.0, 0.0)},
    }

    flow_id = "serverX:burst1"

    # 1) custo novo via B não é suficientemente melhor (apenas ligeiramente melhor)
    msg = FloodingPacket(
        flow_id=flow_id,
        seq=0,
        ts_sent=time.time(),
        rtt_ms=95.0,   # custo ~ 47.5
        loss_pct=0.0,
        stream_ids=["S1"],
    )
    routing._update_routing_from_announce(
        remote_ip="B",
        msg=msg,
        new_rtt_ms=95.0,
        new_loss_pct=0.0,
        neighbor_costs=neighbor_costs,
    )
    # Mantém A como next_hop
    assert node.routing_table["S1"]["next_hop"] == "A"

    # 2) custo muito melhor via B (p.ex 50ms)
    msg2 = FloodingPacket(
        flow_id=flow_id,
        seq=0,
        ts_sent=time.time(),
        rtt_ms=50.0,   # custo 25.0
        loss_pct=0.0,
        stream_ids=["S1"],
    )
    routing._update_routing_from_announce(
        remote_ip="B",
        msg=msg2,
        new_rtt_ms=50.0,
        new_loss_pct=0.0,
        neighbor_costs=neighbor_costs,
    )
    # Agora deve mudar para B
    assert node.routing_table["S1"]["next_hop"] == "B"


# -------------------------------------------------------------------
# TESTES: _check_expired_flows
# -------------------------------------------------------------------

def test_check_expired_flows_finalizes_bursts(monkeypatch):
    node = FakeNode()
    routing = RoutingManager(node)

    remote_ip = "10.0.0.2"
    flow_id = "serverY:burst9"

    with node._flows_lock:
        node.flow_state[(remote_ip, flow_id)] = {
            "from_ip": remote_ip,
            "base_rtt_ms": 10.0,
            "base_loss_pct": 0.0,
            "stream_ids": ["S1"],
            "received": 2,              # já recebeu alguns pacotes
            "min_delay_ms": 5.0,
            "first_time": time.time() - 1.0,  # suficientemente antigo
        }

    called = {"count": 0}

    def fake_finalize(from_ip, fid):
        called["count"] += 1
        # emular o pop que o método real faz
        with node._flows_lock:
            node.flow_state.pop((from_ip, fid), None)

    monkeypatch.setattr(routing, "_finalize_flow_and_reflood", fake_finalize)

    routing._check_expired_flows()

    assert called["count"] == 1
    with node._flows_lock:
        assert (remote_ip, flow_id) not in node.flow_state
