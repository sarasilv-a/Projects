import struct
from protocols.control_types import MessageType, ControlSubtype

class AckPacket:
    """
    ACK genérico para mensagens de controlo enviadas via UDP.

    Formato:
      [type (1 byte)=1]
      [subtype (1 byte)=ACK]
      [orig_subtype (1 byte)]
      [msg_id (4 bytes, uint32)]  -- ID da msg original
    """

    def __init__(self, orig_subtype: int, msg_id: int):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.ACK
        self.orig_subtype = orig_subtype
        self.msg_id = msg_id

    def serialize(self) -> bytes:
        # !BBBI = tipo, subtipo, orig_subtype, msg_id
        return struct.pack("!BBBI", self.tipo, self.subtipo, self.orig_subtype, self.msg_id)

    @staticmethod
    def deserialize(data: bytes) -> "AckPacket":
        if len(data) < 7:
            raise ValueError("Data too short for AckPacket")

        tipo, subtipo, orig_subtype, msg_id = struct.unpack("!BBBI", data[:7])
        if tipo != MessageType.CONTROL:
            raise ValueError(f"Unexpected type for AckPacket: {tipo}")
        if subtipo != ControlSubtype.ACK:
            raise ValueError(f"Unexpected subtype for AckPacket: {subtipo}")

        return AckPacket(orig_subtype, msg_id)
