import struct
from typing import List
from protocols.control_types import MessageType, ControlSubtype


class FloodingPacket:
    """
    ANNOUNCE message used to send burst information from server to client.
    Format:
        [type=1][subtype=3][flow_id_len][flow_id]
        [seq (I)][ts_sent (d)][rtt_ms (f)][loss_pct (f)]
        [num_streams (B)]
          repeated num_streams times:
            [sid_len (B)][sid (UTF-8)]

    - type        = 1 (control)
    - subtype     = 3 (ANNOUNCE)
    - flow_id_len = 1 byte
    - flow_id     = UTF-8 string
    - seq         = 4-byte unsigned int (I)
    - ts_sent     = 8-byte float (d)
    - rtt_ms      = 4-byte float (f) 
    - loss_pct    = 4-byte float (f)
    - num_streams = 1 byte (0-255)
    - sid_len     = 1 byte
    - sid         = UTF-8 string (ID da stream)
    """

    def __init__(
        self,
        flow_id: str,
        seq: int,
        ts_sent: float,
        rtt_ms: float,
        loss_pct: float,
        stream_ids: List[str],
    ):
        self.tipo = MessageType.CONTROL
        self.subtipo = ControlSubtype.ANNOUNCE
        self.flow_id = flow_id
        self.seq = seq
        self.ts_sent = ts_sent
        self.rtt_ms = rtt_ms
        self.loss_pct = loss_pct
        self.stream_ids = [str(s) for s in stream_ids]

    def serialize(self) -> bytes:
        flow_bytes = self.flow_id.encode("utf-8")
        flow_len = len(flow_bytes)
        if flow_len > 255:
            raise ValueError("flow_id too long (max 255 bytes in UTF-8)")

        num_streams = len(self.stream_ids)
        if num_streams > 255:
            raise ValueError("Too many streams (max 255)")

        header = struct.pack("!BBB", self.tipo, self.subtipo, flow_len)

        # seq (I) + ts_sent (d) + rtt_ms (f) + loss_pct (f) + num_streams (B)
        body = flow_bytes + struct.pack(
            "!IdffB",
            self.seq,
            self.ts_sent,
            self.rtt_ms,
            self.loss_pct,
            num_streams,
        )

        # acrescentar cada stream_id
        for sid in self.stream_ids:
            sid_bytes = sid.encode("utf-8")
            sid_len = len(sid_bytes)
            if sid_len > 255:
                raise ValueError("stream_id too long (max 255 bytes in UTF-8)")
            body += struct.pack("!B", sid_len) + sid_bytes

        return header + body

    @staticmethod
    def deserialize(data: bytes) -> "FloodingPacket":
        if len(data) < 3:
            raise ValueError("Data too short for FloodingPacket header")

        tipo, subtipo, flow_len = struct.unpack("!BBB", data[:3])
        if tipo != MessageType.CONTROL or subtipo != ControlSubtype.ANNOUNCE:
            raise ValueError(f"Unexpected type/subtype: {tipo}/{subtipo}")

        # mínimo: header (3) + flow_id + seq(4) + ts_sent(8) + rtt_ms(4) + loss_pct(4) + num_streams(1)
        if len(data) < 3 + flow_len + 4 + 8 + 4 + 4 + 1:
            raise ValueError("Data too short for FloodingPacket body")

        start = 3
        end = 3 + flow_len
        flow_id = data[start:end].decode("utf-8")

        # seq + ts_sent + rtt_ms + loss_pct + num_streams
        seq, ts_sent, rtt_ms, loss_pct, num_streams = struct.unpack(
            "!IdffB", data[end : end + 21]
        )
        offset = end + 21

        stream_ids: list[str] = []
        for _ in range(num_streams):
            if len(data) < offset + 1:
                raise ValueError("Data too short while reading stream_id length")
            sid_len = struct.unpack("!B", data[offset : offset + 1])[0]
            offset += 1
            if len(data) < offset + sid_len:
                raise ValueError("Data too short while reading stream_id bytes")
            sid = data[offset : offset + sid_len].decode("utf-8")
            offset += sid_len
            stream_ids.append(sid)

        return FloodingPacket(flow_id, seq, ts_sent, rtt_ms, loss_pct, stream_ids)
