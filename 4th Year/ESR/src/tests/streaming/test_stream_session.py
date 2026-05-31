from streams.stream_session_packet import StreamSessionPacket


def test_push_packet_increases_queue_and_get_next_packet_order():
    session = StreamSessionPacket(stream_id="S1")  # modo receiver, sem video_path

    # fila começa vazia
    assert list(session._packet_queue) == []

    # push de dois pacotes
    session.push_packet(b"pkt1")
    session.push_packet(b"pkt2")

    # tamanho da fila aumentou
    assert len(session._packet_queue) == 2

    # get_next_packet devolve por ordem de entrada
    first = session.get_next_packet()
    second = session.get_next_packet()
    assert first == b"pkt1"
    assert second == b"pkt2"

    # fila ficou vazia
    assert len(session._packet_queue) == 0


def test_get_next_packet_returns_none_when_empty():
    session = StreamSessionPacket(stream_id="S1")

    # sem nada na fila -> None
    assert session.get_next_packet() is None

    # depois de consumir tudo, volta a None
    session.push_packet(b"pkt")
    assert session.get_next_packet() == b"pkt"
    assert session.get_next_packet() is None
