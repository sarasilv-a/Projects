import threading
import time

import pytest

from config import UDP_PORT
from protocols.stream_list_packet import (
    StreamListRequestPacket,
    StreamListResponsePacket,
)
from protocols.stream_request_packet import (
    StreamRequestPacket,
    StreamResponseMessage,
    RequestMethod,
)
from protocols.control_types import ControlSubtype, MessageType
from protocols.rtp_packet import RtpPacket
from protocols.nack_packet import NackPacket
from transport.streaming import StreamingManager


# -------------------------------------------------------------------
# DUMMIES / STUBS
# -------------------------------------------------------------------

class DummySocket:
    def __init__(self):
        self.sent = []  # lista de (data, addr)

    def sendto(self, data: bytes, addr):
        self.sent.append((data, addr))


class DummyReliable:
    def __init__(self):
        self.calls = []

    def send_with_retries(self, payload, msg_id, dest_ip, orig_subtype, max_retries=5, timeout=None):
        self.calls.append(
            {
                "payload": payload,
                "msg_id": msg_id,
                "dest_ip": dest_ip,
                "orig_subtype": orig_subtype,
                "max_retries": max_retries,
                "timeout": timeout,
            }
        )
        # por default, simular sucesso
        return True


class FakeSession:
    def __init__(self):
        self.packets = []

    def push_packet(self, data: bytes):
        self.packets.append(data)

    def get_next_packet(self):
        if not self.packets:
            return None
        return self.packets.pop(0)


class FakeNode:
    """
    Node mínimo para testar StreamingManager.
    Só expõe os atributos usados em node.streaming.
    """
    def __init__(self, node_id="TestNode"):
        self.node_id = node_id

        # sockets / reliable
        self.udp_sock = DummySocket()
        self.reliable = DummyReliable()

        # locks
        self._streams_lock = threading.Lock()
        self._requests_lock = threading.Lock()
        self._pending_lock = threading.Lock()

        # estado de stream / routing
        self.routing_table = {}
        self.stream_clients = {}      # stream_id -> { client_ip -> {paused: bool} }
        self.local_streams = {}       # stream_id -> Session-like
        self.stream_upstreams = {}    # stream_id -> {active: bool, next_hop: ip}
        self.pending_requests = {}    # req_id -> {response: StreamResponseMessage | None}

        # NACK / RTP
        self.rtp_rx_state = {}        # (upstream_ip, stream_id) -> stats
        self.rtx_history = {}         # (stream_id, client_ip) -> {packets, order}
        self.LOSS_THRESHOLD = 0.0     # para forçar NACK mesmo com 1 perda

        # retransmissão / history
        self.RTX_HISTORY_MAX = 200


# -------------------------------------------------------------------
# STREAM LIST
# -------------------------------------------------------------------

def test_handle_stream_list_request_sends_all_routes():
    node = FakeNode()
    mgr = StreamingManager(node)

    node.routing_table = {
        "S1": {"server_id": "Netflix"},
        "S2": {"server_id": "HBO"},
    }

    req = StreamListRequestPacket(req_id=123, client_id="clientX")
    remote_ip = "10.0.0.2"

    mgr.handle_stream_list_request(remote_ip, req)

    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    assert addr == (remote_ip, UDP_PORT)

    resp = StreamListResponsePacket.deserialize(data)
    assert resp.req_id == 123
    # A ordem pode variar, por isso usamos set()
    assert set(resp.entries) == {("S1", "Netflix"), ("S2", "HBO")}


# -------------------------------------------------------------------
# STREAM REQUEST: PLAY / PAUSE / TEARDOWN
# -------------------------------------------------------------------

def test_handle_stream_request_play_success(monkeypatch):
    node = FakeNode()
    mgr = StreamingManager(node)

    stream_id = "S1"
    client_ip = "10.0.0.10"
    upstream_ip = "10.0.0.9"

    # rota conhecida
    node.routing_table[stream_id] = {"next_hop": upstream_ip, "server_id": "Srv1"}

    # impedir que o helper _request_stream_from_upstream faça coisas reais
    called = {}

    def fake_req_upstream(sid, nh):
        called["sid"] = sid
        called["nh"] = nh

    monkeypatch.setattr(mgr, "_request_stream_from_upstream", fake_req_upstream)

    req = StreamRequestPacket(
        req_id=1,
        client_id="clientX",
        stream_id=stream_id,
        method=RequestMethod.PLAY,
    )

    mgr.handle_stream_request(client_ip, req)

    # cliente registado
    assert stream_id in node.stream_clients
    assert client_ip in node.stream_clients[stream_id]
    assert node.stream_clients[stream_id][client_ip]["paused"] is False

    # upstream e sessão criados
    assert stream_id in node.stream_upstreams
    assert node.stream_upstreams[stream_id]["next_hop"] == upstream_ip
    assert node.stream_upstreams[stream_id]["active"] is True
    assert stream_id in node.local_streams

    # helper foi chamado
    assert called["sid"] == stream_id
    assert called["nh"] == upstream_ip

    # resposta OK
    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    assert addr == (client_ip, UDP_PORT)
    resp = StreamResponseMessage.deserialize(data)
    assert resp.status == 0
    assert resp.message == "OK"


def test_handle_stream_request_play_no_route_or_loop():
    node = FakeNode()
    mgr = StreamingManager(node)

    stream_id = "S1"
    client_ip = "10.0.0.10"

    # cenário 1: sem rota nenhuma
    req = StreamRequestPacket(
        req_id=2,
        client_id="clientX",
        stream_id=stream_id,
        method=RequestMethod.PLAY,
    )

    mgr.handle_stream_request(client_ip, req)

    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    resp = StreamResponseMessage.deserialize(data)
    assert resp.status == 1
    assert "No route" in resp.message

    # não criou upstream
    assert stream_id not in node.stream_upstreams

    # cenário 2: rota existe mas next_hop == client -> proteção de loop
    node.udp_sock.sent.clear()
    node.routing_table[stream_id] = {"next_hop": client_ip}
    mgr.handle_stream_request(client_ip, req)

    data, addr = node.udp_sock.sent[0]
    resp = StreamResponseMessage.deserialize(data)
    assert resp.status == 1
    assert "No route" in resp.message


def test_handle_stream_request_pause():
    node = FakeNode()
    mgr = StreamingManager(node)

    stream_id = "S1"
    client_ip = "10.0.0.10"

    node.stream_clients[stream_id] = {client_ip: {"paused": False}}

    req = StreamRequestPacket(
        req_id=3,
        client_id="clientX",
        stream_id=stream_id,
        method=RequestMethod.PAUSE,
    )

    mgr.handle_stream_request(client_ip, req)

    assert node.stream_clients[stream_id][client_ip]["paused"] is True

    assert len(node.udp_sock.sent) == 1
    data, addr = node.udp_sock.sent[0]
    resp = StreamResponseMessage.deserialize(data)
    assert resp.status == 0
    assert resp.message == "PAUSED"


def test_handle_stream_request_teardown_triggers_upstream_teardown(monkeypatch):
    node = FakeNode()
    mgr = StreamingManager(node)

    stream_id = "S1"
    client_ip = "10.0.0.10"
    upstream_ip = "10.0.0.9"

    node.stream_clients[stream_id] = {client_ip: {"paused": False}}
    node.stream_upstreams[stream_id] = {"next_hop": upstream_ip, "active": True}

    called = {}

    def fake_teardown_upstream(sid, nh, cleanup=True):
        called["sid"] = sid
        called["nh"] = nh
        called["cleanup"] = cleanup

    monkeypatch.setattr(mgr, "_send_teardown_upstream", fake_teardown_upstream)

    req = StreamRequestPacket(
        req_id=4,
        client_id="clientX",
        stream_id=stream_id,
        method=RequestMethod.TEARDOWN,
    )

    mgr.handle_stream_request(client_ip, req)

    # cliente removido
    assert client_ip not in node.stream_clients[stream_id]

    # como era o único cliente, TEARDOWN upstream chamado
    assert called["sid"] == stream_id
    assert called["nh"] == upstream_ip

    # resposta TEARDOWN
    data, addr = node.udp_sock.sent[0]
    resp = StreamResponseMessage.deserialize(data)
    assert resp.status == 0
    assert resp.message == "TEARDOWN"


# -------------------------------------------------------------------
# STREAM RESPONSE
# -------------------------------------------------------------------

def test_handle_stream_response_sets_pending_and_clears_pending_control():
    node = FakeNode()
    mgr = StreamingManager(node)

    req_id = 123
    remote_ip = "10.0.0.2"

    with node._requests_lock:
        node.pending_requests[req_id] = {"response": None}

    with node._pending_lock:
        node._pending_control = {(remote_ip, req_id): {"retries": 1}}

    resp = StreamResponseMessage(req_id=req_id, status=0, message="OK")

    mgr.handle_stream_response(resp, (remote_ip, UDP_PORT))

    with node._requests_lock:
        assert node.pending_requests[req_id]["response"] is resp

    with node._pending_lock:
        assert (remote_ip, req_id) not in node._pending_control


# -------------------------------------------------------------------
# STREAM PACKETS & NACK
# -------------------------------------------------------------------

def make_stream_packet(stream_id: str, seq: int, payload: bytes = b"x") -> bytes:
    """
    Cria um pacote no formato:
      [MessageType.STREAM][sid_len][sid][RTP(header+payload)]
    """
    rtp = RtpPacket()
    rtp.encode(
        version=2,
        padding=0,
        extension=0,
        cc=0,
        seqnum=seq,
        marker=0,
        pt=96,
        ssrc=1,
        payload=payload,
    )
    rtp_bytes = rtp.getPacket()
    sid_bytes = stream_id.encode("utf-8")
    data = bytearray()
    data.append(MessageType.STREAM)
    data.append(len(sid_bytes))
    data.extend(sid_bytes)
    data.extend(rtp_bytes)
    return bytes(data)


def test_handle_stream_packet_sends_nack_and_pushes_to_session():
    node = FakeNode()
    mgr = StreamingManager(node)

    remote_ip = "10.0.0.9"
    stream_id = "S1"

    # upstream ativo e esperado
    node.stream_upstreams[stream_id] = {"active": True, "next_hop": remote_ip}
    session = FakeSession()
    node.local_streams[stream_id] = session

    # ------------------------------------------------------------------
    # O código tem warmup (20 pkts) em que ignora gaps para evitar NACKs
    # quando um upstream começa "a meio". Portanto: primeiro consumimos warmup.
    # ------------------------------------------------------------------

    # Envia 20 pacotes sequenciais (seq=1..20) para esgotar warmup
    for seq in range(1, 21):
        pkt = make_stream_packet(stream_id, seq=seq)
        mgr.handle_stream_packet(remote_ip, pkt)

    # Agora introduz um gap: seq=22 (falta o 21) -> warmup já terminou => deve enviar NACK
    pkt_gap = make_stream_packet(stream_id, seq=22)
    mgr.handle_stream_packet(remote_ip, pkt_gap)

    # sessão recebeu todos os pacotes (21 no total: 1..20 e 22)
    assert len(session.packets) == 21
    assert session.packets[-1] == pkt_gap

    # deve ter enviado pelo menos 1 NACK (LOSS_THRESHOLD=0.0)
    assert len(node.udp_sock.sent) >= 1
    data, addr = node.udp_sock.sent[-1]
    assert addr == (remote_ip, UDP_PORT)

    nack = NackPacket.deserialize(data)
    assert nack.stream_id == stream_id
    assert nack.first_seq == 21
    assert nack.last_seq == 21


def test_handle_stream_packet_ignores_unexpected_upstream():
    node = FakeNode()
    mgr = StreamingManager(node)

    remote_ip = "10.0.0.9"
    other_ip = "10.0.0.8"
    stream_id = "S1"

    # upstream configurado para outro IP
    node.stream_upstreams[stream_id] = {"active": True, "next_hop": other_ip}
    session = FakeSession()
    node.local_streams[stream_id] = session

    pkt = make_stream_packet(stream_id, seq=1)
    mgr.handle_stream_packet(remote_ip, pkt)

    # não deve guardar o pacote porque veio de IP inesperado
    assert session.packets == []
    assert node.udp_sock.sent == []


# -------------------------------------------------------------------
# HANDLE NACK
# -------------------------------------------------------------------

def test_handle_nack_retransmits_range():
    node = FakeNode()
    mgr = StreamingManager(node)

    remote_ip = "10.0.0.2"
    stream_id = "S1"

    key = (stream_id, remote_ip)
    pkt10 = b"packet10"
    pkt11 = b"packet11"
    node.rtx_history[key] = {
        "packets": {10: pkt10, 11: pkt11},
        "order": [10, 11],
    }

    nack = NackPacket(stream_id, first_seq=10, last_seq=11)
    mgr.handle_nack(remote_ip, nack)

    # foram enviadas duas retransmissões
    assert len(node.udp_sock.sent) == 2
    sent_payloads = [d for (d, addr) in node.udp_sock.sent]
    assert pkt10 in sent_payloads
    assert pkt11 in sent_payloads


# -------------------------------------------------------------------
# RELIABLE REQUEST HELPERS
# -------------------------------------------------------------------

def test_send_stream_request_success(monkeypatch):
    node = FakeNode()
    mgr = StreamingManager(node)

    dest_ip = "10.0.0.2"
    stream_id = "S1"

    # evitar sleeps
    import transport.streaming as s_mod
    monkeypatch.setattr(s_mod.time, "sleep", lambda s: None)

    # _wait_for_response devolve logo uma resposta dummy
    dummy_resp = StreamResponseMessage(req_id=0, status=0, message="OK")
    monkeypatch.setattr(mgr, "_wait_for_response", lambda req_id, timeout_total=2.0: dummy_resp)

    ack_ok, resp = mgr._send_stream_request(dest_ip, stream_id, RequestMethod.PLAY)

    assert ack_ok is True
    assert resp is dummy_resp

    # pending_requests deve estar vazio no fim
    assert node.pending_requests == {}

    # reliable.send_with_retries foi chamado
    assert len(node.reliable.calls) == 1
    call = node.reliable.calls[0]
    assert call["dest_ip"] == dest_ip
    assert call["orig_subtype"] == ControlSubtype.REQUEST


def test_send_teardown_upstream_cleans_state(monkeypatch):
    node = FakeNode()
    mgr = StreamingManager(node)

    stream_id = "S1"
    next_hop = "10.0.0.9"

    node.stream_upstreams[stream_id] = {"next_hop": next_hop, "active": True}
    node.local_streams[stream_id] = FakeSession()

    # fazer _send_stream_request devolve (True, resp_dummy)
    def fake_send_stream_request(dest_ip, sid, method):
        return True, StreamResponseMessage(req_id=1, status=0, message="BYE")

    monkeypatch.setattr(mgr, "_send_stream_request", fake_send_stream_request)

    mgr._send_teardown_upstream(stream_id, next_hop, cleanup=True)

    # como cleanup=True e next_hop bate certo, remove estado de stream
    assert stream_id not in node.stream_upstreams
    assert stream_id not in node.local_streams
