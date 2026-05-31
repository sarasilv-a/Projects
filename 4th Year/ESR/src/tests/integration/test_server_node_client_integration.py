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
        # regista sempre
        self.sent.append((data, addr))
        # se houver hook, chama-o (p.ex. para entregar diretamente ao Node)
        if self.hook is not None:
            self.hook(data, addr)

    def recvfrom(self, bufsize: int):
        raise OSError("recvfrom not supported in DummySocket for this test")


def test_server_node_client_end_to_end_frame(monkeypatch):
    """
    Integração leve:
      - Server gera 1 frame RTP para o Node
      - Node recebe via handle_stream_packet
      - Node reenviaria para o client (mini-implementação do stream_loop)
      - payload visto pelo "client" coincide com o frame do VideoStream.
    """

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
            # Node recebe pacote STREAM do upstream
            node.streaming.handle_stream_packet(server_ip, data)

    srv.udp_sock.hook = server_to_node_hook

    # 8) Configurar o Node para servir o client neste stream
    # Normalmente seria via REQUEST/ANNOUNCE, aqui setamos diretamente
    node.stream_clients[stream_id] = {client_ip: {"paused": False}}
    node.stream_upstreams[stream_id] = {"active": True, "next_hop": server_ip}

    # Fake "sessão" local (buffer) para o Node
    from streams.stream_session_packet import StreamSessionPacket
    node.local_streams[stream_id] = StreamSessionPacket(stream_id)

    # 9) Preparar captura do lado do "client"
    client_packets = []

    def node_sendto(data: bytes, addr):
        # regista os envios que vão para o client
        dest_ip, dest_port = addr
        if dest_ip == client_ip and dest_port == UDP_PORT:
            client_packets.append(data)

    node.udp_sock.sendto = node_sendto

    # 10) Server envia 1 frame RTP para o Node
    # dummy event que faz o loop de _send_rtp_stream parar após 1 iteração
    class DummyEvent:
        def __init__(self):
            self.called = 0

        def wait(self, timeout: float) -> bool:
            # na primeira chamada não pára, na segunda pára
            self.called += 1
            return self.called > 1

    stop_event = DummyEvent()
    srv.streaming._send_rtp_stream(stream_id, node_ip, stop_event)

    # Neste ponto:
    #  - Server enviou pacote STREAM para node_ip
    #  - hook chamou node.streaming.handle_stream_packet(...)
    #  - o RTP ficou em node.local_streams[stream_id]

    # 11) Fazer uma mini-iteração do que stream_loop faria:
    session = node.local_streams[stream_id]
    packet = session.get_next_packet()
    assert packet is not None  # recebeu algo do server

    # packet formato: [STREAM][sid_len][sid][RTP]
    assert packet[0] == MessageType.STREAM
    sid_len = packet[1]
    sid = packet[2 : 2 + sid_len].decode("utf-8")
    assert sid == stream_id

    # reenviar para o client (1 cliente ativo)
    node.udp_sock.sendto(packet, (client_ip, UDP_PORT))

    # 12) Verificar o que o "client" recebeu
    assert len(client_packets) == 1
    client_packet = client_packets[0]

    # Deve ter o mesmo formato [STREAM][sid_len][sid][RTP]
    assert client_packet[0] == MessageType.STREAM
    sid_len_c = client_packet[1]
    sid_c = client_packet[2 : 2 + sid_len_c].decode("utf-8")
    assert sid_c == stream_id

    rtp_bytes = client_packet[2 + sid_len_c :]
    rtp = RtpPacket()
    rtp.decode(rtp_bytes)

    # payload no client deve ser o frame original
    payload = rtp.getPayload()
    assert payload == b"HELLO_FRAME"
