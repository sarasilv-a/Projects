import time
import os
import socket
import threading
import random

from config import UDP_PORT
from streams.stream_session_packet import StreamSessionPacket

try:
    from .server_control import ServerControl
    from .server_net_loop import ServerNetLoop
    from .server_streaming import ServerStreaming
except ImportError:
    # quando corres como script (sem package)
    from server_control import ServerControl
    from server_net_loop import ServerNetLoop
    from server_streaming import ServerStreaming

class Server:
    def __init__(self, config):
        self.node_id = config["id"]
        self.role = config.get("role")
        self.neighbors = config.get("neighbors", [])
        self.stream_ids = config.get("streams", [])

        self._global_seq = 0

        self._pending_control = {}
        self._pending_lock = threading.Lock()

        # Track active streams: stream_id -> set of IPs
        self._active_streams = {}
        self._active_streams_lock = threading.Lock()

        # Track streaming threads per stream/IP
        self._stream_threads = {}
        self._stream_threads_lock = threading.Lock()

        # socket UDP
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(("0.0.0.0", UDP_PORT))

        # --- RETRANSMISSÕES RTP ---
        self.rtx_history = {}
        self.RTX_HISTORY_MAX = 200

        # módulos
        self.control = ServerControl(self)
        self.net = ServerNetLoop(self)
        self.streaming = ServerStreaming(self)

        self.stream_sessions = self.get_stream_sessions(self.stream_ids)

    def run(self):
        self.control.send_join_to_neighbors()

        flood_thread = threading.Thread(target=self.control.server_flood_loop, daemon=True)
        flood_thread.start()

        request_thread = threading.Thread(target=self.net.udp_loop, daemon=True)
        request_thread.start()

        stream_thread = threading.Thread(target=self.streaming.streaming_loop, daemon=True)
        stream_thread.start()

        while True:
            time.sleep(1)

    def get_stream_sessions(self, stream_ids):
        return self.streaming.get_stream_sessions(stream_ids)
