from streams.video_stream import VideoStream
from collections import deque
import threading

class StreamSessionPacket:
    """
    Modo servidor:
      - é criada com (stream_id, video_path, ssrc)
      - lê frames do ficheiro via VideoStream.next_frame()
      - codifica em RTP e envia.

    Modo nó/cliente (receiver):
      - é criada só com (stream_id)
      - não tem video_path nem VideoStream
      - apenas guarda/fornece pacotes já prontos (RTP + header de tipo).
    """

    def __init__(self, stream_id: str, video_path: str = None, ssrc: int = None):
        self.stream_id = stream_id

        # Modo servidor: temos video_path -> abrir VideoStream
        if video_path is not None:
            self.video = VideoStream(video_path)
        else:
            self.video = None

        self.ssrc = ssrc if ssrc is not None else 0
        self.seqnum = 0
        self.running = False
        self.subscribers = 0

        # Modo receiver: fila de pacotes (bytes) para reenviar
        self._packet_queue = deque()
        self._queue_lock = threading.Lock()

    # --------- API para o servidor (produtor de frames) ---------
    def next_frame(self):
        """
        Devolve o próximo frame de vídeo (só faz sentido no servidor).
        """
        if self.video is None:
            return None
        return self.video.nextFrame()

    # --------- API para nós/cliente (consumer/relay de pacotes) ---------
    def push_packet(self, packet: bytes):
        """
        Guarda um pacote completo (tipo + RTP) na fila.
        Usado pelo nó quando recebe STREAM do servidor.
        """
        with self._queue_lock:
            self._packet_queue.append(packet)

    def get_next_packet(self):
        """
        Retorna o próximo pacote da fila, ou None se estiver vazia.
        Usado pelo nó para reenviar para os clientes.
        """
        with self._queue_lock:
            if self._packet_queue:
                return self._packet_queue.popleft()
            return None
