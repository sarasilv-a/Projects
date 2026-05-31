import pytest

from config import UDP_PORT
from protocols.control_types import MessageType
from protocols.rtp_packet import RtpPacket


class DummySocket:
    def __init__(self, *args, **kwargs):
        self.bound = None
        self.sent = []  # lista de (data, addr)
        self.hook = None  # função opcional para "entregar" o pacote a outro componente

    def bind(self, addr):
        self.bound = addr

    def sendto(self, data: bytes, addr):
        self.sent.append((data, addr))
        if self.hook is not None:
            self.hook(data, addr)

    def recvfrom(self, bufsize: int):
        raise OSError("recvfrom not supported in DummySocket for this test")


def test_server_node_client_end_to_end_frame(monkeypatch):
    # 1) Pachar socket.socket para DummySocket (Server e Node)
    monkeypatch.setattr(
        "socket.socket",
        lambda *args, **kwargs: DummySocket(*args, **kwargs),
        raising=True,
    )

    # 2) Importar Server e Node depois do patch
    from server.server import Server
    import server.server_streaming as sstream_mod
    from transport.node import Node

    # 3) Dummy VideoStream para o server (um único frame)
    frames = [b"HELLO_FRAME"]

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

    # 4) Criar Server com config mínima (sem streams para não abrir ficheiros reais)
    cfg_server = {"id": "SrvTest", "role": "server", "neighbors": [], "streams": []}
    srv = Server(cfg_server)

    # 5) Criar Node (transport) com config simples
    cfg_node = {"id": "NodeX", "role": "router", "neighbors": []}
    node = Node(cfg_node)

    # IPs lógicos
    server_ip = "10.0.0.1"
    node_ip = "10.0.0.2"
    client_ip = "10.0.0.99"

    # 6) stream_id e sessão RTP do server
    stream_id = "movie.Mjpeg"

    class DummySession:
        def __init__(self):
            self.seqnum = 0
            self.ssrc = 1234

    srv.stream_sessions = {stream_id: DummySession()}

    # 7) Ligar o socket do Server ao Node: sendto do Server -> handle_stream_packet do Node
    def server_to_node_hook(data: bytes, addr):
        dest_ip, dest_port = addr
        if dest_ip == node_ip and dest_port == UDP_PORT:
            node.streaming.handle_stream_packet(server_ip, data)

    srv.udp_sock.hook = server_to_node_hook

    # 8) Configurar o Node para servir o client neste stream
    node.stream_clients[stream_id] = {client_ip: {"paused": False}}
    node.stream_upstreams[stream_id] = {"active": True, "next_hop": server_ip}

    from streams.stream_session_packet import StreamSessionPacket
    node.local_streams[stream_id] = StreamSessionPacket(stream_id)

    # 9) Captura do lado do "client"
    client_packets = []

    def node_sendto(data: bytes, addr):
        dest_ip, dest_port = addr
        if dest_ip == client_ip and dest_port == UDP_PORT:
            client_packets.append(data)

    node.udp_sock.sendto = node_sendto

    # 10) Server envia 1 frame RTP para o Node
    class DummyEvent:
        def __init__(self):
            self.called = 0

        def wait(self, timeout: float) -> bool:
            self.called += 1
            return self.called > 1

    stop_event = DummyEvent()
    srv.streaming._send_rtp_stream(stream_id, node_ip, stop_event)

    # 11) Mini-iter do loop do node: tirar da sessão e reenviar ao client
    session = node.local_streams[stream_id]
    packet = session.get_next_packet()
    assert packet is not None

    assert packet[0] == MessageType.STREAM
    sid_len = packet[1]
    sid = packet[2 : 2 + sid_len].decode("utf-8")
    assert sid == stream_id

    node.udp_sock.sendto(packet, (client_ip, UDP_PORT))

    # 12) Verificar o que o "client" recebeu
    assert len(client_packets) == 1
    client_packet = client_packets[0]

    assert client_packet[0] == MessageType.STREAM
    sid_len_c = client_packet[1]
    sid_c = client_packet[2 : 2 + sid_len_c].decode("utf-8")
    assert sid_c == stream_id

    rtp_bytes = client_packet[2 + sid_len_c :]
    rtp = RtpPacket()
    rtp.decode(rtp_bytes)

    assert rtp.getPayload() == b"HELLO_FRAME"
