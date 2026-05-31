import struct
from protocols.control_types import MessageType, ControlSubtype

class NeighborControlPacket:
    """
    Generic JOIN/LEAVE control message.

    Binary format (UDP, confiável):
      [type (1 byte)=1]
      [subtype (1 byte)=5|6]
      [msg_id (4 bytes, uint32)]  -- ID único da mensagem
    """

    def __init__(self, subtype: int, msg_id: int):
        self.tipo = MessageType.CONTROL
        self.subtipo = subtype
        self.msg_id = msg_id

    def serialize(self) -> bytes:
        # !BBI = type (B), subtype (B), msg_id (I)
        return struct.pack("!BBI", self.tipo, self.subtipo, self.msg_id)

    @staticmethod
    def deserialize(data: bytes) -> "NeighborControlPacket":
        if len(data) < 6:
            raise ValueError("Data too short for NeighborControlPacket")

        tipo, subtipo, msg_id = struct.unpack("!BBI", data[:6])
        if tipo != MessageType.CONTROL:
            raise ValueError(f"Unexpected type: {tipo}")
        if subtipo not in (ControlSubtype.JOIN, ControlSubtype.LEAVE):
            raise ValueError(f"Unexpected control subtype: {subtipo}")

        return NeighborControlPacket(subtipo, msg_id)


class JoinPacket(NeighborControlPacket):
    def __init__(self, msg_id: int):
        super().__init__(ControlSubtype.JOIN, msg_id)


class LeavePacket(NeighborControlPacket):
    def __init__(self, msg_id: int):
        super().__init__(ControlSubtype.LEAVE, msg_id)
