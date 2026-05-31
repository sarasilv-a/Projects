import struct
from protocols.control_types import MessageType, ControlSubtype


class NackPacket:
    """
    NACK genérico para pedir retransmissão de intervalos de seq RTP
    numa dada stream.

    Formato:
      [type (1 byte) = CONTROL]
      [subtype (1 byte) = NACK]
      [stream_id_len (1 byte)]
      [stream_id (stream_id_len bytes, utf-8)]
      [first_seq (2 bytes, uint16)]
      [last_seq  (2 bytes, uint16)]
    """

    def __init__(self, stream_id: str, first_seq: int, last_seq: int):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.NACK
        self.stream_id = stream_id
        self.first_seq = first_seq
        self.last_seq = last_seq

    def serialize(self) -> bytes:
        sid_bytes = self.stream_id.encode("utf-8")
        sid_len = len(sid_bytes)
        header = struct.pack("!BBB", self.tipo, self.subtipo, sid_len)
        tail = struct.pack("!HH", self.first_seq & 0xFFFF, self.last_seq & 0xFFFF)
        return header + sid_bytes + tail

    @staticmethod
    def deserialize(data: bytes) -> "NackPacket":
        if len(data) < 1 + 1 + 1 + 2 + 2:
            raise ValueError("Data too short for NackPacket")

        tipo, subtipo, sid_len = struct.unpack("!BBB", data[:3])
        if tipo != MessageType.CONTROL:
            raise ValueError(f"Unexpected type for NackPacket: {tipo}")
        if subtipo != ControlSubtype.NACK:
            raise ValueError(f"Unexpected subtype for NackPacket: {subtipo}")

        expected_len = 3 + sid_len + 2 + 2
        if len(data) < expected_len:
            raise ValueError("Data too short for given stream_id_len in NackPacket")

        offset = 3
        sid_bytes = data[offset:offset + sid_len]
        stream_id = sid_bytes.decode("utf-8")
        offset += sid_len

        first_seq, last_seq = struct.unpack("!HH", data[offset:offset + 4])
        return NackPacket(stream_id, first_seq, last_seq)
