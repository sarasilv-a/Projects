import time
import threading

import pytest

from config import UDP_PORT
from protocols.control_types import ControlSubtype
from protocols.neighbor_control_packet import JoinPacket, LeavePacket
from protocols.heartbeat_packet import HeartbeatPing, HeartbeatPong
from protocols.ack_packet import AckPacket
from transport.heartbeat import HeartbeatManager


# -------------------------------------------------------------------
# DUMMIES / STUBS
# -------------------------------------------------------------------

class DummySocket:
    def __init__(self):
        self.sent = []  # lista de (data, addr)

    def sendto(self, data: bytes, addr):
        self.sent.append((data, addr))


class DummyRouting:
    def __init__(self):
        self.last_withdraw = None

    def propagate_route_withdraw(self, stream_ids, origin_ip: str):
        # guarda o último withdraw propagado
        self.last_withdraw = (tuple(stream_ids), origin_ip)


class FakeNode:
    """
    Node minimalista com o mínimo de atributos que o HeartbeatManager usa.
    Não abre sockets reais nem threads.
    """
    def __init__(self, node_id="TestNode"):
        self.node_id = node_id
        self.neighbors = []
        self._lock = threading.Lock()

        # heartbeat state
        self._hb_state = {}       # ip -> {"missed": int, "last_pong": ts}
        self.dead_cooldown = {}   # ip -> ignore_until (epoch)
        self.last_rtt = {}        # ip -> rtt_ms

        # ping tracking
        self._pending_pings = {}  # (ip, ping_id) -> sent_ts
        self._ping_lock = threading.Lock()

        # routing / flows
        self.routing = DummyRouting()
        self.routing_table = {}      # stream_id -> { next_hop: ip, ... }
        self.neighbor_history = {}   # flow_id -> { ip -> deque([...]) }
        self.flow_state = {}         # (from_ip, flow_id) -> {...}
        self._flows_lock = threading.Lock()

        # UDP socket “dummy”
        self.udp_sock = DummySocket()


# -------------------------------------------------------------------
# TESTES
# -------------------------------------------------------------------

def test_join_adds_neighbor_and_sends_ack():
    node = FakeNode()
    hb = HeartbeatManager(node)

    remote_ip = "10.0.0.2"
    msg = JoinPacket(msg_id=123)

    hb.handle_join_leave(remote_ip, msg)

    # Vizinho foi adicionado
    assert remote_ip in node.neighbors
    # Estado de heartbeat inicializado
    assert remote_ip in node._hb_state
    assert node._hb_state[remote_ip]["missed"] == 0

    # Um ACK foi enviado para o remote_ip
    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    assert addr == (remote_ip, UDP_PORT)

    ack = AckPacket.deserialize(data)
    assert ack.orig_subtype == ControlSubtype.JOIN
    assert ack.msg_id == msg.msg_id


def test_leave_removes_neighbor_and_sends_ack():
    node = FakeNode()
    remote_ip = "10.0.0.2"

    # prepara estado como se já fosse vizinho
    node.neighbors.append(remote_ip)
    node._hb_state[remote_ip] = {"missed": 2, "last_pong": time.time()}
    node.last_rtt[remote_ip] = 12.3
    node.routing_table["S1"] = {"next_hop": remote_ip}
    node.routing_table["S2"] = {"next_hop": "10.0.0.99"}  # deve ficar

    # flows e pings pendentes
    node.flow_state[(remote_ip, "F1")] = {"dummy": True}
    node.flow_state[("other", "F2")] = {"dummy": True}
    node._pending_pings[(remote_ip, 1)] = time.time()
    node._pending_pings[("other", 2)] = time.time()

    hb = HeartbeatManager(node)

    msg = LeavePacket(msg_id=456)
    hb.handle_join_leave(remote_ip, msg)

    # vizinho removido
    assert remote_ip not in node.neighbors
    assert remote_ip not in node._hb_state
    assert remote_ip not in node.last_rtt

    # rotas que usavam esse vizinho foram removidas
    assert "S1" not in node.routing_table
    # rotas de outros next_hop permanecem
    assert "S2" in node.routing_table

    # flow_state limpo para esse from_ip
    assert (remote_ip, "F1") not in node.flow_state
    # flows de outros vizinhos mantidos
    assert ("other", "F2") in node.flow_state

    # pings pendentes desse ip removidos
    assert all(key[0] != remote_ip for key in node._pending_pings.keys())

    # Um ACK(LEAVE) foi enviado
    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    assert addr == (remote_ip, UDP_PORT)
    ack = AckPacket.deserialize(data)
    assert ack.orig_subtype == ControlSubtype.LEAVE
    assert ack.msg_id == msg.msg_id

    # Se havia streams removidas, o withdraw foi propagado
    # (no nosso caso, S1 tinha next_hop remote_ip)
    assert node.routing.last_withdraw is not None
    streams, origin_ip = node.routing.last_withdraw
    assert "S1" in streams
    assert origin_ip == remote_ip


def test_ping_adds_new_neighbor_and_sends_pong():
    node = FakeNode()
    hb = HeartbeatManager(node)

    remote_ip = "10.0.0.3"
    ping = HeartbeatPing(ping_id=77)

    # não está em dead_cooldown, nem em neighbors
    assert remote_ip not in node.neighbors

    hb.handle_ping(remote_ip, ping)

    # passou a ser vizinho
    assert remote_ip in node.neighbors
    # estado de heartbeat criado / actualizado
    assert remote_ip in node._hb_state
    assert node._hb_state[remote_ip]["missed"] == 0

    # foi enviado um PONG de volta
    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    assert addr == (remote_ip, UDP_PORT)
    pong = HeartbeatPong.deserialize(data)
    assert pong.ping_id == ping.ping_id


def test_ping_ignored_during_dead_cooldown():
    node = FakeNode()
    hb = HeartbeatManager(node)

    remote_ip = "10.0.0.4"
    ping = HeartbeatPing(ping_id=88)

    # marcar este ip como "morto" com cooldown no futuro
    node.dead_cooldown[remote_ip] = time.time() + 60.0

    hb.handle_ping(remote_ip, ping)

    # não deve ser re-adicionado como neighbor
    assert remote_ip not in node.neighbors
    # não deve ter estado de hb criado
    assert remote_ip not in node._hb_state
    # (podes relaxar isto se no teu código ainda envias PONG mesmo ignorando o add)


def test_pong_updates_rtt_and_resets_missed():
    node = FakeNode()
    hb = HeartbeatManager(node)

    remote_ip = "10.0.0.5"
    ping_id = 42

    # simular ping enviado há 100ms
    sent_ts = time.time() - 0.1
    with node._ping_lock:
        node._pending_pings[(remote_ip, ping_id)] = sent_ts

    # estado de hb existente com alguns misses
    with node._lock:
        node.neighbors.append(remote_ip)
        node._hb_state[remote_ip] = {"missed": 3, "last_pong": sent_ts - 1}

    pong = HeartbeatPong(ping_id=ping_id)
    hb.handle_pong(remote_ip, pong)

    # entrada em _pending_pings removida
    with node._ping_lock:
        assert (remote_ip, ping_id) not in node._pending_pings

    # RTT calculado
    assert remote_ip in node.last_rtt
    assert node.last_rtt[remote_ip] >= 0.0

    # missed resetado a 0 e last_pong actualizado
    with node._lock:
        st = node._hb_state[remote_ip]
        assert st["missed"] == 0
        assert st["last_pong"] > sent_ts
