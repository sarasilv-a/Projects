# tests/reliable/test_reliable_ctrl.py
import threading
import time

import pytest

from config import UDP_PORT
from protocols.ack_packet import AckPacket
from protocols.control_types import ControlSubtype
from transport.reliable_ctrl import ReliableControlManager


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
        # devolve em segundos um valor "default_ms * factor"
        return (default_ms * factor) / 1000.0


class FakeNode:
    """
    Node mínimo para testar o ReliableControlManager.
    """
    def __init__(self, node_id="TestNode"):
        self.node_id = node_id

        self._pending_lock = threading.Lock()
        self._pending_control = {}

        self.udp_sock = DummySocket()
        self.heartbeat = DummyHeartbeat()


# -------------------------------------------------------------------
# TESTES: handle_ack
# -------------------------------------------------------------------

def test_handle_ack_removes_pending_entry():
    node = FakeNode()
    mgr = ReliableControlManager(node)

    remote_ip = "10.0.0.2"
    msg_id = 123

    key = (remote_ip, msg_id)
    with node._pending_lock:
        node._pending_control[key] = {
            "retries": 1,
            "failed": False,
            "orig_subtype": ControlSubtype.REQUEST,
        }

    ack = AckPacket(orig_subtype=ControlSubtype.REQUEST, msg_id=msg_id)

    mgr.handle_ack(remote_ip, ack)

    with node._pending_lock:
        assert key not in node._pending_control


# -------------------------------------------------------------------
# TESTES: send_with_retries (sucesso)
# -------------------------------------------------------------------

def test_send_with_retries_success_ack_on_first_send(monkeypatch):
    node = FakeNode()
    mgr = ReliableControlManager(node)

    dest_ip = "10.0.0.2"
    msg_id = 42
    payload = b"hello"

    # patch ao sleep para acelerar testes (não dormir de verdade)
    import transport.reliable_ctrl as rc_mod
    monkeypatch.setattr(rc_mod.time, "sleep", lambda s: None)

    # Simula ACK logo ao primeiro sendto:
    # remove a entrada de _pending_control como se o handler tivesse corrido.
    def fake_sendto(data, addr):
        assert addr == (dest_ip, UDP_PORT)
        with node._pending_lock:
            node._pending_control.pop((dest_ip, msg_id), None)
        node.udp_sock.sent.append((data, addr))

    node.udp_sock.sent = []
    monkeypatch.setattr(node.udp_sock, "sendto", fake_sendto)

    ok = mgr.send_with_retries(
        payload=payload,
        msg_id=msg_id,
        dest_ip=dest_ip,
        orig_subtype=ControlSubtype.REQUEST,
        max_retries=3,
        timeout=0.01,  # timeout pequenino para não bloquear
    )

    assert ok is True
    # Apenas 1 envio foi suficiente
    assert len(node.udp_sock.sent) == 1


# -------------------------------------------------------------------
# TESTES: send_with_retries (falha, sem ACK)
# -------------------------------------------------------------------

def test_send_with_retries_failure_no_ack(monkeypatch):
    node = FakeNode()
    mgr = ReliableControlManager(node)

    dest_ip = "10.0.0.3"
    msg_id = 99
    payload = b"test"

    import transport.reliable_ctrl as rc_mod
    monkeypatch.setattr(rc_mod.time, "sleep", lambda s: None)

    # apenas regista envios, mas NUNCA remove _pending_control -> sem ACK
    send_calls = []

    def fake_sendto(data, addr):
        assert addr == (dest_ip, UDP_PORT)
        send_calls.append((data, addr))

    monkeypatch.setattr(node.udp_sock, "sendto", fake_sendto)

    ok = mgr.send_with_retries(
        payload=payload,
        msg_id=msg_id,
        dest_ip=dest_ip,
        orig_subtype=ControlSubtype.REQUEST,
        max_retries=2,
        timeout=0.01,
    )

    # sem ACK -> deve retornar False
    assert ok is False
    # foi tentado enviar pelo menos max_retries vezes
    assert len(send_calls) >= 2

    # entrada deve ter sido removida no fim
    with node._pending_lock:
        assert (dest_ip, msg_id) not in node._pending_control


# -------------------------------------------------------------------
# TESTE: dest_ip vazio
# -------------------------------------------------------------------

def test_send_with_retries_invalid_dest_ip():
    node = FakeNode()
    mgr = ReliableControlManager(node)

    ok = mgr.send_with_retries(
        payload=b"xxx",
        msg_id=1,
        dest_ip="",  # IP inválido -> early return
        orig_subtype=ControlSubtype.REQUEST,
    )

    assert ok is False
    # não deve criar entradas em _pending_control
    assert node._pending_control == {}
