import time
import os
import threading

from config import UDP_PORT
from streams.stream_session_packet import StreamSessionPacket
from streams.video_stream import VideoStream
from protocols.control_types import MessageType
from protocols.rtp_packet import RtpPacket


class ServerStreaming:
    def __init__(self, server):
        self.s = server

    def get_stream_sessions(self, stream_ids):
        s = self.s
        sessions: dict[str, StreamSessionPacket] = {}
        for sid in stream_ids:
            video_path = os.path.join("server/streams", str(sid))
            ssrc = int(time.time() * 1000) & 0xFFFFFFFF
            sessions[sid] = StreamSessionPacket(stream_id=sid, video_path=video_path, ssrc=ssrc)
        return sessions

    def streaming_loop(self):
        s = self.s
        print(f"[{s.node_id}] Streaming loop started")

        while True:
            time.sleep(0.01)

            with s._active_streams_lock:
                for stream_id, ip_set in list(s._active_streams.items()):
                    if not ip_set:
                        del s._active_streams[stream_id]
                        continue

                    for remote_ip in ip_set:
                        stream_key = (stream_id, remote_ip)

                        with s._stream_threads_lock:
                            if stream_key not in s._stream_threads:
                                event = threading.Event()
                                thread = threading.Thread(
                                    target=self._send_rtp_stream,
                                    args=(stream_id, remote_ip, event),
                                    daemon=True,
                                )

                                s._stream_threads[stream_key] = {"event": event, "thread": thread}
                                thread.start()

                                print(f"[{s.node_id}] Started RTP thread for stream {stream_id} -> {remote_ip}")

    def _send_rtp_stream(self, stream_id: str, remote_ip: str, event: threading.Event):
        s = self.s
        print(f"[{s.node_id}] RTP streaming thread started for {stream_id} -> {remote_ip}")

        session = s.stream_sessions.get(stream_id)
        if not session:
            print(f"[{s.node_id}] Stream session {stream_id} not found")
            return

        video_path = os.path.join("server/streams", str(stream_id))
        try:
            local_video = VideoStream(video_path)
        except IOError as e:
            print(f"[{s.node_id}] Cannot open video file {video_path}: {e}")
            return

        FRAME_RATE = 20
        FRAME_INTERVAL = 1.0 / FRAME_RATE

        while True:
            if event.wait(FRAME_INTERVAL):
                print(f"[{s.node_id}] Stopping RTP stream {stream_id} -> {remote_ip}")
                break

            frame_data = local_video.nextFrame()

            if frame_data is None:
                print(f"[{s.node_id}] Video {stream_id} ended, restarting for {remote_ip}")
                local_video.release()
                try:
                    local_video = VideoStream(video_path)
                except IOError as e:
                    print(f"[{s.node_id}] Cannot reopen video file {video_path}: {e}")
                    break
                continue

            session.seqnum += 1
            rtp = RtpPacket()
            rtp.encode(
                version=2, padding=0, extension=0, cc=0,
                seqnum=session.seqnum, marker=0, pt=26, ssrc=session.ssrc,
                payload=frame_data,
            )
            seq = session.seqnum

            stream_id_bytes = stream_id.encode("utf-8")
            if len(stream_id_bytes) > 255:
                print(f"[{s.node_id}] stream_id too long")
                return

            full_packet = (
                bytes([MessageType.STREAM]) +
                bytes([len(stream_id_bytes)]) +
                stream_id_bytes +
                rtp.getPacket()
            )

            # guardar no history para retransmissões
            key = (stream_id, remote_ip)
            hist = s.rtx_history.setdefault(key, {"packets": {}, "order": []})

            hist["packets"][seq] = full_packet
            hist["order"].append(seq)
            if len(hist["order"]) > s.RTX_HISTORY_MAX:
                oldest = hist["order"].pop(0)
                hist["packets"].pop(oldest, None)

            print(f"[Server - Print 1 ] sending full packet stream to {remote_ip}")

            try:
                print(f"[Server] sending full packet stream to {remote_ip}")
                s.udp_sock.sendto(full_packet, (remote_ip, UDP_PORT))
            except OSError as e:
                print(f"[{s.node_id}] Error sending RTP to {remote_ip}: {e}")

        local_video.release()

        stream_key = (stream_id, remote_ip)
        with s._stream_threads_lock:
            s._stream_threads.pop(stream_key, None)

        with s._active_streams_lock:
            if stream_id in s._active_streams:
                s._active_streams[stream_id].discard(remote_ip)

        print(f"[{s.node_id}] RTP streaming thread ended for {stream_id} -> {remote_ip}")
