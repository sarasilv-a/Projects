import struct
from protocols.control_types import MessageType, ControlSubtype

class RouteWithdrawPacket:
    """
    Mensagem fiável (com ACK) para anunciar que este nó deixou de ter rota
    para um certo conjunto de stream_ids.

    Formato binário:
      [type   (1 byte) = MessageType.CONTROL]
      [subtype(1 byte) = ControlSubtype.ROUTE_WITHDRAW]
      [msg_id (4 bytes, uint32)]  -- ID único da mensagem (para ACK)
      [n      (2 bytes, uint16)]  número de streams
      repetido n vezes:
        [len   (2 bytes, uint16)] tamanho do stream_id em bytes
        [id    (len bytes)]       stream_id em UTF-8
    """

    def __init__(self, msg_id: int, stream_ids):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.ROUTE_WITHDRAW
        self.msg_id = msg_id
        self.stream_ids = list(stream_ids)

    def serialize(self) -> bytes:
        parts = [struct.pack("!BBIH", self.tipo, self.subtipo, self.msg_id, len(self.stream_ids))]
        for sid in self.stream_ids:
            b = sid.encode("utf-8")
            parts.append(struct.pack("!H", len(b)))
            parts.append(b)
        return b"".join(parts)

    @staticmethod
    def deserialize(data: bytes) -> "RouteWithdrawPacket":
        if len(data) < 8:
            raise ValueError("Data too short for RouteWithdrawPacket")

        tipo, subtipo, msg_id, n = struct.unpack("!BBIH", data[:8])
        if tipo != MessageType.CONTROL:
            raise ValueError(f"Unexpected type for RouteWithdrawPacket: {tipo}")
        if subtipo != ControlSubtype.ROUTE_WITHDRAW:
            raise ValueError(f"Unexpected subtype for RouteWithdrawPacket: {subtipo}")

        stream_ids = []
        offset = 8
        for _ in range(n):
            if len(data) < offset + 2:
                raise ValueError("Truncated RouteWithdrawPacket (len)")
            (length,) = struct.unpack("!H", data[offset:offset+2])
            offset += 2
            if len(data) < offset + length:
                raise ValueError("Truncated RouteWithdrawPacket (id)")
            sid_bytes = data[offset:offset+length]
            offset += length
            stream_ids.append(sid_bytes.decode("utf-8"))

        return RouteWithdrawPacket(msg_id, stream_ids)
