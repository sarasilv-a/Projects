import struct
from protocols.control_types import MessageType, ControlSubtype


class RequestMethod:
    SETUP = 1
    PLAY = 2
    PAUSE = 3
    TEARDOWN = 4

class StreamRequestPacket:
    """REQUEST control message: client asks server to PLAY/PAUSE/TEARDOWN a stream.

    Binary format:
      [type (1 byte)=1]
      [subtype (1 byte)=8]
      [req_id (4 bytes, unsigned int)]
      [method (1 byte)]               # 2=PLAY, 3=PAUSE, 4=TEARDOWN
      [client_id_len (1 byte)]
      [client_id (UTF-8)]
      [stream_id_len (1 byte)]
      [stream_id (UTF-8)]
    """

    def __init__(
        self,
        req_id: int,
        client_id: str,
        stream_id: str,
        method: int,
    ):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.REQUEST
        self.req_id = req_id
        self.client_id = client_id
        self.stream_id = stream_id
        self.method = method

    def serialize(self) -> bytes:
        if not (0 <= self.req_id <= 0xFFFFFFFF):
            raise ValueError("req_id must be in 0..2^32-1")
        if self.method not in (
            RequestMethod.SETUP,
            RequestMethod.PLAY,
            RequestMethod.PAUSE,
            RequestMethod.TEARDOWN,
        ):
            raise ValueError("invalid method")

        client_bytes = self.client_id.encode("utf-8")
        stream_bytes = self.stream_id.encode("utf-8")

        if len(client_bytes) > 255:
            raise ValueError("client_id too long (max 255 bytes)")
        if len(stream_bytes) > 255:
            raise ValueError("stream_id too long (max 255 bytes)")

        # type, subtype, req_id, method
        header = struct.pack("!BBIB", self.tipo, self.subtipo, self.req_id, self.method)
        body = (
            struct.pack("!B", len(client_bytes)) + client_bytes +
            struct.pack("!B", len(stream_bytes)) + stream_bytes
        )
        return header + body

    @staticmethod
    def deserialize(data: bytes) -> "StreamRequestPacket":
        # min size: 1+1+4+1+1+1 = 9 bytes
        if len(data) < 9:
            raise ValueError("Data too short for StreamRequestPacket")

        tipo, subtipo, req_id, method = struct.unpack("!BBIB", data[:7])
        if tipo != MessageType.CONTROL:
            raise ValueError(f"Unexpected type: {tipo}")
        if subtipo != ControlSubtype.REQUEST:
            raise ValueError(f"Unexpected control subtype: {subtipo}")
        if method not in (
            RequestMethod.SETUP,
            RequestMethod.PLAY,
            RequestMethod.PAUSE,
            RequestMethod.TEARDOWN,
        ):
            raise ValueError(f"Invalid method: {method}")

        offset = 7

        # client_id
        client_len = data[offset]
        offset += 1
        if len(data) < offset + client_len + 1:
            raise ValueError("Data too short for client_id")

        client_id = data[offset:offset + client_len].decode("utf-8")
        offset += client_len

        # stream_id
        stream_len = data[offset]
        offset += 1
        if len(data) < offset + stream_len:
            raise ValueError("Data too short for stream_id")

        stream_id = data[offset:offset + stream_len].decode("utf-8")

        return StreamRequestPacket(
            req_id=req_id,
            client_id=client_id,
            stream_id=stream_id,
            method=method,
        )


class StreamResponseMessage:
    """RESPONSE control message: server answers a StreamRequest.

    Binary format:
      [type (1 byte)=1]
      [subtype (1 byte)=9]
      [req_id (4 bytes, unsigned int)]   # echoes the request
      [status (1 byte)]                  # 0=OK, >0=error
      [msg_len (1 byte)]
      [message (UTF-8)]
    """

    def __init__(self, req_id: int, status: int, message: str = ""):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.RESPONSE
        self.req_id = req_id
        self.status = status
        self.message = message

    def serialize(self) -> bytes:
        if not (0 <= self.req_id <= 0xFFFFFFFF):
            raise ValueError("req_id must be in 0..2^32-1")
        if not (0 <= self.status <= 255):
            raise ValueError("status must be in 0..255")

        msg_bytes = self.message.encode("utf-8")
        if len(msg_bytes) > 255:
            raise ValueError("message too long (max 255 bytes)")

        header = struct.pack("!BBI", self.tipo, self.subtipo, self.req_id)
        body = struct.pack("!BB", self.status, len(msg_bytes)) + msg_bytes
        return header + body

    @staticmethod
    def deserialize(data: bytes) -> "StreamResponseMessage":
        if len(data) < 8:
            raise ValueError("Data too short for StreamResponseMessage")

        tipo, subtipo, req_id = struct.unpack("!BBI", data[:6])
        if tipo != MessageType.CONTROL:
            raise ValueError(f"Unexpected type: {tipo}")
        if subtipo != ControlSubtype.RESPONSE:
            raise ValueError(f"Unexpected control subtype: {subtipo}")

        offset = 6
        status, msg_len = struct.unpack("!BB", data[offset:offset + 2])
        offset += 2

        if len(data) < offset + msg_len:
            raise ValueError("Data too short for message")

        message = data[offset:offset + msg_len].decode("utf-8")

        return StreamResponseMessage(req_id, status, message)
