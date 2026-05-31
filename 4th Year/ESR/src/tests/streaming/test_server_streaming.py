import types

import pytest

from config import UDP_PORT
from protocols.control_types import MessageType
from protocols.rtp_packet import RtpPacket
from server.server import Server              # módulo certo
import server.server_streaming as sstream_mod # monkeypatch no módulo certo


class DummySocket:
    def __init__(self):
        self.sent = []  # lista de (data, addr)

    def sendto(self, data: bytes, addr):
        self.sent.append((data, addr))


class DummySession:
    def __init__(self, ssrc=1234, seqnum=0):
        self.ssrc = ssrc
        self.seqnum = seqnum  # vai sendo incrementado pelo server


class DummyEvent:
    """
    Event fake: faz N ciclos de envio e depois devolve True para parar o loop.
    Também regista os timeouts recebidos.
    """
    def __init__(self, stop_after: int):
        self.stop_after = stop_after
        self.counter = 0
        self.timeouts = []

    def wait(self, timeout: float) -> bool:
        self.timeouts.append(timeout)
        if self.counter >= self.stop_after:
            return True  # parar loop
        self.counter += 1
        return False


def test_send_rtp_stream_creates_rtp_packets_and_uses_interval(monkeypatch):
    # 1) Pachar VideoStream dentro do módulo server.server_streaming (onde ele é importado)
    frames = [b"F1", b"F2", b"F3"]

    class DummyVideoStream:
        def __init__(self, filename):
            self._frames = frames.copy()
            self.released = False

        def nextFrame(self):
            if self._frames:
                return self._frames.pop(0)
            return None

        def release(self):
            self.released = True

    monkeypatch.setattr(sstream_mod, "VideoStream", DummyVideoStream, raising=True)

    # 2) Criar config mínima sem streams para evitar abrir ficheiros no __init__
    cfg = {"id": "SrvTest", "role": "server", "neighbors": [], "streams": []}
    srv = Server(cfg)

    # 3) Substituir socket real por DummySocket
    dummy_sock = DummySocket()
    srv.udp_sock = dummy_sock

    # 4) Injetar uma sessão fake para o stream_id
    stream_id = "movie.Mjpeg"
    remote_ip = "10.0.0.42"
    session = DummySession(ssrc=9999, seqnum=0)
    srv.stream_sessions = {stream_id: session}

    # rtx_history deve começar vazio
    assert srv.rtx_history == {}

    # 5) Criar evento fake para fazer p.ex. 3 iterações de envio
    event = DummyEvent(stop_after=3)

    # 6) Chamar _send_rtp_stream no módulo de streaming (agora vive lá)
    srv.streaming._send_rtp_stream(stream_id, remote_ip, event)

    # --- Verificações ---

    # 3 frames -> 3 envios UDP
    assert len(dummy_sock.sent) == 3

    stream_id_bytes = stream_id.encode("utf-8")
    sid_len = len(stream_id_bytes)

    for i, (packet, addr) in enumerate(dummy_sock.sent, start=1):
        assert addr == (remote_ip, UDP_PORT)

        # header de stream
        assert packet[0] == MessageType.STREAM
        assert packet[1] == sid_len
        assert packet[2 : 2 + sid_len] == stream_id_bytes

        # RTP
        rtp_bytes = packet[2 + sid_len :]
        rtp = RtpPacket()
        rtp.decode(rtp_bytes)

        # seqnum deve ser 1,2,3 ...
        assert rtp.seqNum() == i

        # payload é o frame correspondente
        assert rtp.getPayload() == frames[i - 1]

    # sessão partilhada deve ter seqnum == 3 no fim
    assert session.seqnum == 3

    # rtx_history deve ter registado estes 3 pacotes
    key = (stream_id, remote_ip)
    assert key in srv.rtx_history
    hist = srv.rtx_history[key]
    assert hist["order"] == [1, 2, 3]
    assert set(hist["packets"].keys()) == {1, 2, 3}

    # timeouts usados em event.wait devem bater com FRAME_INTERVAL = 1/20
    assert len(event.timeouts) >= 3
    for t in event.timeouts[:3]:
        assert pytest.approx(t, rel=1e-3) == 1.0 / 20.0
