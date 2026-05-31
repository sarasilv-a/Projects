from time import time

HEADER_SIZE = 12


class RtpPacket:
    """
    Simplified RTP packet for UDP streaming.
    """

    def __init__(self):
        self.header = bytearray(HEADER_SIZE)
        self.payload = b""

    def encode(self, version, padding, extension, cc,
               seqnum, marker, pt, ssrc, payload: bytes):
        """Encode the RTP packet with header fields and payload."""
        timestamp = int(time())
        header = bytearray(HEADER_SIZE)

        # Byte 0
        header[0] = (header[0] | (version << 6)) & 0xC0  # 2 bits
        header[0] = header[0] | (padding << 5)           # 1 bit
        header[0] = header[0] | (extension << 4)         # 1 bit
        header[0] = header[0] | (cc & 0x0F)              # 4 bits

        # Byte 1
        header[1] = header[1] | (marker << 7)            # 1 bit
        header[1] = header[1] | (pt & 0x7F)              # 7 bits

        # Seq num
        header[2] = (seqnum >> 8) & 0xFF
        header[3] = seqnum & 0xFF

        # Timestamp
        header[4] = (timestamp >> 24) & 0xFF
        header[5] = (timestamp >> 16) & 0xFF
        header[6] = (timestamp >> 8) & 0xFF
        header[7] = timestamp & 0xFF

        # SSRC
        header[8] = (ssrc >> 24) & 0xFF
        header[9] = (ssrc >> 16) & 0xFF
        header[10] = (ssrc >> 8) & 0xFF
        header[11] = ssrc & 0xFF

        self.header = header
        self.payload = payload

    def decode(self, byte_stream: bytes):
        """Decode the RTP packet."""
        self.header = bytearray(byte_stream[:HEADER_SIZE])
        self.payload = byte_stream[HEADER_SIZE:]

    def version(self):
        """Return RTP version."""
        return int(self.header[0] >> 6)

    def seqNum(self):
        """Return sequence (frame) number."""
        seq_num = (self.header[2] << 8) | self.header[3]
        return int(seq_num)

    def timestamp(self):
        """Return timestamp."""
        timestamp = (
            (self.header[4] << 24)
            | (self.header[5] << 16)
            | (self.header[6] << 8)
            | self.header[7]
        )
        return int(timestamp)

    def payloadType(self):
        """Return payload type."""
        pt = self.header[1] & 0x7F
        return int(pt)

    def getPayload(self) -> bytes:
        """Return payload."""
        return self.payload

    def getPacket(self) -> bytes:
        """Return RTP packet (header + payload)."""
        return bytes(self.header) + self.payload

    def printheader(self):
        print(f"[RTP Packet] Version: {self.version()}, Seq: {self.seqNum()}, TS: {self.timestamp()}, PT: {self.payloadType()}")
