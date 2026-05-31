import socket
import threading
import os
import time
import random

from config import UDP_PORT
from client_net_loop import ClientNetLoop
from client_stream import ClientStream
from client_ui import ClientUI


class Client:
    def __init__(self, config):
        self.client_id = config["id"]
        self.role = config.get("role")
        self.neighbors = config.get("neighbors", [])

        # por simplicidade, assumimos 1 vizinho principal
        self.neighbor_ip = self.neighbors[0] if self.neighbors else None

        self.connected = False

        self.CTRL_PORT = UDP_PORT

        # socket UDP
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(("0.0.0.0", UDP_PORT))

        # controlo/reliability
        self._pending_control = {}
        self._pending_lock = threading.Lock()

        # pedidos pendentes (req_id -> {"response": ...})
        self.pending_requests = {}
        self._requests_lock = threading.Lock()

        # Streaming state
        self.current_stream_id = None
        self.frame_nbr = 0
        self.streaming_active = False
        self.stream_lock = threading.Lock()

        # GUI legacy
        self.gui_root = None
        self.video_label = None

        # Cache file para frames (usado pelo ClientGUI)
        self.cache_file = f"cache-{self.client_id}.jpg"

        # estado de receção para a stream atual
        self.rtp_rx_state = {"last_seq": None, "expected": 0, "received": 0}
        self.LOSS_THRESHOLD = 0.05  # 5%

        # módulos
        self.stream = ClientStream(self)
        self.net = ClientNetLoop(self, self.stream)
        self.ui = ClientUI(self)

        # thread UDP
        t = threading.Thread(target=self.net.udp_loop, daemon=True)
        t.start()

    # -------- API pública --------

    def join_network(self):
        return self.net.join_network()

    def leave_network(self):
        return self.net.leave_network()

    def menu_loop(self):
        return self.ui.menu_loop()

    def request_stream_list(self):
        return self.net.request_stream_list()

    def play_stream(self):
        return self.stream.play_stream()

    def pause_stream(self):
        return self.stream.pause_stream()

    def stop_stream(self):
        return self.stream.stop_stream()

    # mantido por compat / GUI legacy
    def start_gui(self):
        return self.stream.start_gui()

    def on_gui_close(self):
        return self.stream.on_gui_close()

