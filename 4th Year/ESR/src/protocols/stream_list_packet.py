import struct
from typing import List, Tuple
from protocols.control_types import MessageType, ControlSubtype


class StreamListRequestPacket:
    """
    Pedido de lista de streams ao nó/servidor.

    Formato binário:
      [type   (1 byte) = MessageType.CONTROL]
      [subtype(1 byte) = ControlSubtype.STREAM_LIST_REQUEST]
      [req_id (4 bytes, unsigned int)]
      [client_id_len (1 byte)]
      [client_id (UTF-8)]
    """

    def __init__(self, req_id: int, client_id: str):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.STREAM_LIST_REQUEST
        self.req_id = req_id
        self.client_id = client_id

    def serialize(self) -> bytes:
        if not (0 <= self.req_id <= 0xFFFFFFFF):
            raise ValueError("req_id must be in 0..2^32-1")

        client_bytes = self.client_id.encode("utf-8")
        if len(client_bytes) > 255:
            raise ValueError("client_id too long (max 255 bytes)")

        header = struct.pack("!BBI", self.tipo, self.subtipo, self.req_id)
        body = struct.pack("!B", len(client_bytes)) + client_bytes
        return header + body

    @staticmethod
    def deserialize(data: bytes) -> "StreamListRequestPacket":
        # min: 1 + 1 + 4 + 1 = 7 bytes
        if len(data) < 7:
            raise ValueError("Data too short for StreamListRequestPacket")

        tipo, subtipo, req_id = struct.unpack("!BBI", data[:6])
        if tipo != MessageType.CONTROL:
            raise ValueError(f"Unexpected type: {tipo}")
        if subtipo != ControlSubtype.STREAM_LIST_REQUEST:
            raise ValueError(f"Unexpected control subtype: {subtipo}")

        offset = 6
        client_len = data[offset]
        offset += 1

        if len(data) < offset + client_len:
            raise ValueError("Data too short for client_id")

        client_id = data[offset:offset + client_len].decode("utf-8")

        return StreamListRequestPacket(req_id=req_id, client_id=client_id)


class StreamListResponsePacket:
    """
    Resposta com lista de streams e respetivo servidor.

    Formato binário:
      [type   (1 byte) = MessageType.CONTROL]
      [subtype(1 byte) = ControlSubtype.STREAM_LIST_RESPONSE]
      [req_id (4 bytes, unsigned int)]     # ecoa o pedido
      [count  (1 byte) = N streams]
      N vezes:
        [stream_id_len (1 byte)]
        [stream_id (UTF-8)]
        [server_id_len (1 byte)]
        [server_id (UTF-8)]
    """

    def __init__(self, req_id: int, entries: List[Tuple[str, str]]):
        """
        entries: lista de (stream_id, server_id)
        """
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.STREAM_LIST_RESPONSE
        self.req_id = req_id
        self.entries = entries

    def serialize(self) -> bytes:
        if not (0 <= self.req_id <= 0xFFFFFFFF):
            raise ValueError("req_id must be in 0..2^32-1")

        if len(self.entries) > 255:
            raise ValueError("too many entries (max 255)")

        header = struct.pack("!BBI", self.tipo, self.subtipo, self.req_id)
        body = bytearray()
        body.append(len(self.entries))

        for stream_id, server_id in self.entries:
            s_bytes = stream_id.encode("utf-8")
            srv_bytes = server_id.encode("utf-8")
            if len(s_bytes) > 255:
                raise ValueError("stream_id too long (max 255 bytes)")
            if len(srv_bytes) > 255:
                raise ValueError("server_id too long (max 255 bytes)")

            body.append(len(s_bytes))
            body.extend(s_bytes)
            body.append(len(srv_bytes))
            body.extend(srv_bytes)

        return header + bytes(body)

    @staticmethod
    def deserialize(data: bytes) -> "StreamListResponsePacket":
        # min: 1+1+4+1 = 7 bytes
        if len(data) < 7:
            raise ValueError("Data too short for StreamListResponsePacket")

        tipo, subtipo, req_id = struct.unpack("!BBI", data[:6])
        if tipo != MessageType.CONTROL:
            raise ValueError(f"Unexpected type: {tipo}")
        if subtipo != ControlSubtype.STREAM_LIST_RESPONSE:
            raise ValueError(f"Unexpected control subtype: {subtipo}")

        offset = 6
        count = data[offset]
        offset += 1

        entries: List[Tuple[str, str]] = []

        for _ in range(count):
            if len(data) < offset + 1:
                raise ValueError("Data too short reading stream_id_len")
            s_len = data[offset]
            offset += 1
            if len(data) < offset + s_len + 1:
                raise ValueError("Data too short for stream_id")
            stream_id = data[offset:offset + s_len].decode("utf-8")
            offset += s_len

            srv_len = data[offset]
            offset += 1
            if len(data) < offset + srv_len:
                raise ValueError("Data too short for server_id")
            server_id = data[offset:offset + srv_len].decode("utf-8")
            offset += srv_len

            entries.append((stream_id, server_id))

        return StreamListResponsePacket(req_id=req_id, entries=entries)
