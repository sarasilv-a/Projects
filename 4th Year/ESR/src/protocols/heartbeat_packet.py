import struct
from protocols.control_types import MessageType, ControlSubtype

class HeartbeatPing:
    """
    [type=1][subtype=PING][ping_id (uint32)]
    """
    def __init__(self, ping_id: int):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.PING
        self.ping_id = ping_id

    def serialize(self) -> bytes:
        return struct.pack("!BBI", self.tipo, self.subtipo, self.ping_id)

    @staticmethod
    def deserialize(data: bytes) -> "HeartbeatPing":
        if len(data) < 6:
            raise ValueError("Data too short for HeartbeatPing")
        tipo, subtipo, ping_id = struct.unpack("!BBI", data[:6])
        if tipo != MessageType.CONTROL or subtipo != ControlSubtype.PING:
            raise ValueError("Unexpected type/subtype in HeartbeatPing")
        return HeartbeatPing(ping_id)


class HeartbeatPong:
    """
    [type=1][subtype=PONG][ping_id (uint32)]  -- copia o ping_id recebido
    """
    def __init__(self, ping_id: int):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.PONG
        self.ping_id = ping_id

    def serialize(self) -> bytes:
        return struct.pack("!BBI", self.tipo, self.subtipo, self.ping_id)

    @staticmethod
    def deserialize(data: bytes) -> "HeartbeatPong":
        if len(data) < 6:
            raise ValueError("Data too short for HeartbeatPong")
        tipo, subtipo, ping_id = struct.unpack("!BBI", data[:6])
        if tipo != MessageType.CONTROL or subtipo != ControlSubtype.PONG:
            raise ValueError("Unexpected type/subtype in HeartbeatPong")
        return HeartbeatPong(ping_id)
