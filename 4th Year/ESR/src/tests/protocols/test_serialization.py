import time
import math

from protocols.control_types import MessageType, ControlSubtype
from protocols.ack_packet import AckPacket
from protocols.heartbeat_packet import HeartbeatPing, HeartbeatPong
from protocols.neighbor_control_packet import JoinPacket, LeavePacket, NeighborControlPacket
from protocols.flooding_packet import FloodingPacket
from protocols.stream_request_packet import (
    StreamRequestPacket,
    StreamResponseMessage,
    RequestMethod,
)
from protocols.stream_list_packet import (
    StreamListRequestPacket,
    StreamListResponsePacket,
)
from protocols.nack_packet import NackPacket
from protocols.route_withdraw_packet import RouteWithdrawPacket
from protocols.rtp_packet import RtpPacket


# ---------- helpers ----------

def approx_equal(a: float, b: float, eps: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=eps, abs_tol=eps)


# ---------- control_types “sanity checks” ----------

def test_message_type_values():
    # estes valores são importantes porque são usados em todos os headers
    assert MessageType.CONTROL == 1
    assert MessageType.STREAM == 2


def test_control_subtype_some_values():
    # não precisamos testar todos, só garantir alguns críticos
    assert ControlSubtype.ACK > 0
    assert ControlSubtype.PING != ControlSubtype.PONG
    assert ControlSubtype.REQUEST != ControlSubtype.RESPONSE


# ---------- ACK ----------

def test_ack_roundtrip():
    orig = AckPacket(orig_subtype=ControlSubtype.REQUEST, msg_id=1234)
    data = orig.serialize()
    parsed = AckPacket.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.ACK
    assert parsed.orig_subtype == ControlSubtype.REQUEST
    assert parsed.msg_id == 1234


# ---------- HEARTBEAT (PING / PONG) ----------

def test_ping_roundtrip():
    orig = HeartbeatPing(ping_id=42)
    data = orig.serialize()
    parsed = HeartbeatPing.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.PING
    assert parsed.ping_id == 42


def test_pong_roundtrip():
    orig = HeartbeatPong(ping_id=99)
    data = orig.serialize()
    parsed = HeartbeatPong.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.PONG
    assert parsed.ping_id == 99


# ---------- JOIN / LEAVE ----------

def test_join_roundtrip_via_neighborcontrol():
    msg_id = 111
    join = JoinPacket(msg_id=msg_id)
    data = join.serialize()

    parsed = NeighborControlPacket.deserialize(data)

    assert parsed.subtipo == ControlSubtype.JOIN
    assert parsed.msg_id == msg_id


def test_leave_roundtrip_via_neighborcontrol():
    msg_id = 222
    leave = LeavePacket(msg_id=msg_id)
    data = leave.serialize()

    parsed = NeighborControlPacket.deserialize(data)

    assert parsed.subtipo == ControlSubtype.LEAVE
    assert parsed.msg_id == msg_id


# ---------- FLOW_ANNOUNCE ----------

def test_flow_announce_roundtrip():
    flow_id = "server1:burst42"
    seq = 7
    ts = time.time()
    rtt_ms = 12.34
    loss_pct = 5.67
    streams = ["netflix", "hgtv"]

    orig = FloodingPacket(
        flow_id=flow_id,
        seq=seq,
        ts_sent=ts,
        rtt_ms=rtt_ms,
        loss_pct=loss_pct,
        stream_ids=streams,
    )

    data = orig.serialize()
    parsed = FloodingPacket.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.ANNOUNCE
    assert parsed.flow_id == flow_id
    assert parsed.seq == seq
    assert approx_equal(parsed.ts_sent, ts, eps=1e-4)
    assert approx_equal(parsed.rtt_ms, rtt_ms, eps=1e-5)
    assert approx_equal(parsed.loss_pct, loss_pct, eps=1e-5)
    assert parsed.stream_ids == streams


# ---------- STREAM REQUEST / RESPONSE ----------

def test_stream_request_roundtrip():
    orig = StreamRequestPacket(
        req_id=123,
        client_id="node-A",
        stream_id="netflix",
        method=RequestMethod.PLAY,
    )
    data = orig.serialize()
    parsed = StreamRequestPacket.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.REQUEST
    assert parsed.req_id == 123
    assert parsed.client_id == "node-A"
    assert parsed.stream_id == "netflix"
    assert parsed.method == RequestMethod.PLAY


def test_stream_response_roundtrip():
    orig = StreamResponseMessage(
        req_id=555,
        status=0,
        message="OK",
    )
    data = orig.serialize()
    parsed = StreamResponseMessage.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.RESPONSE
    assert parsed.req_id == 555
    assert parsed.status == 0
    assert parsed.message == "OK"


# ---------- STREAM LIST REQUEST / RESPONSE ----------

def test_stream_list_request_roundtrip():
    orig = StreamListRequestPacket(req_id=999, client_id="fernando")
    data = orig.serialize()
    parsed = StreamListRequestPacket.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.STREAM_LIST_REQUEST
    assert parsed.req_id == 999
    assert parsed.client_id == "fernando"


def test_stream_list_response_roundtrip():
    entries = [("netflix", "server1"), ("hbo", "server2")]
    orig = StreamListResponsePacket(req_id=123, entries=entries)
    data = orig.serialize()
    parsed = StreamListResponsePacket.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.STREAM_LIST_RESPONSE
    assert parsed.req_id == 123
    assert parsed.entries == entries


# ---------- NACK ----------

def test_nack_roundtrip():
    orig = NackPacket(stream_id="netflix", first_seq=10, last_seq=20)
    data = orig.serialize()
    parsed = NackPacket.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.NACK
    assert parsed.stream_id == "netflix"
    assert parsed.first_seq == 10
    assert parsed.last_seq == 20


# ---------- ROUTE_WITHDRAW ----------

def test_route_withdraw_roundtrip():
    stream_ids = ["netflix", "hbo"]
    orig = RouteWithdrawPacket(msg_id=321, stream_ids=stream_ids)
    data = orig.serialize()
    parsed = RouteWithdrawPacket.deserialize(data)

    assert parsed.tipo == MessageType.CONTROL
    assert parsed.subtipo == ControlSubtype.ROUTE_WITHDRAW
    assert parsed.msg_id == 321
    assert parsed.stream_ids == stream_ids


# ---------- RTP PACKET (não é “control” mas é protocolo) ----------

def test_rtp_packet_encode_decode():
    # Criar um pacote RTP com campos conhecidos
    payload = b"hello-rtp"
    version = 2
    padding = 0
    extension = 0
    cc = 0
    seqnum = 1234
    marker = 0
    pt = 96
    ssrc = 42

    pkt = RtpPacket()
    pkt.encode(
        version=version,
        padding=padding,
        extension=extension,
        cc=cc,
        seqnum=seqnum,
        marker=marker,
        pt=pt,
        ssrc=ssrc,
        payload=payload,
    )

    encoded = pkt.getPacket()

    # Decodificar noutro objeto
    pkt2 = RtpPacket()
    pkt2.decode(encoded)

    assert pkt2.version() == version
    assert pkt2.seqNum() == seqnum
    assert pkt2.payloadType() == pt
    assert pkt2.getPayload() == payload

    # timestamp é gerado com time(), por isso só verificamos que é int > 0
    assert isinstance(pkt2.timestamp(), int)
    assert pkt2.timestamp() > 0


# ---------- TESTES DE ERRO BÁSICOS ----------

def test_ack_deserialize_invalid_type_raises():
    msg = AckPacket(orig_subtype=ControlSubtype.REQUEST, msg_id=1)
    data = bytearray(msg.serialize())
    data[0] = 0xFF  # tipo inválido

    import pytest
    with pytest.raises(ValueError):
        AckPacket.deserialize(bytes(data))


def test_stream_list_request_too_short_raises():
    import pytest
    with pytest.raises(ValueError):
        StreamListRequestPacket.deserialize(b"\x01\x01")  # claramente curto
