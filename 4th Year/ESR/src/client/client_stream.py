import os
from tkinter import Tk, Label, Frame, Button, LEFT
from PIL import Image, ImageTk

from config import UDP_PORT
from protocols.control_types import MessageType
from protocols.rtp_packet import RtpPacket
from protocols.nack_packet import NackPacket
from protocols.stream_request_packet import RequestMethod


class ClientStream:
    def __init__(self, client):
        self.client = client

    # ------------------------------------------------------------
    # STREAM packet handler
    # ------------------------------------------------------------
    def handle_stream_packet(self, data: bytes, remote_ip: str):
        c = self.client

        print(f"[CLIENT {c.client_id}] STREAM packet detected, streaming_active={c.streaming_active}")

        with c.stream_lock:
            if not c.streaming_active:
                print(f"[CLIENT {c.client_id}] Discarding STREAM packet - not actively streaming")
                return

        if len(data) < 2:
            return

        sid_len = data[1]
        if len(data) < 2 + sid_len + 1:
            return

        sid = data[2:2 + sid_len].decode("utf-8")

        with c.stream_lock:
            if c.current_stream_id and sid != c.current_stream_id:
                print(f"[CLIENT {c.client_id}] Ignoring STREAM for {sid}, current={c.current_stream_id}")
                return

        rtp_bytes = data[2 + sid_len:]
        rtp_packet = RtpPacket()

        print(f"[CLIENT {c.client_id}] Attempting to decode RTP packet ({len(rtp_bytes)} bytes)")

        try:
            rtp_packet.decode(rtp_bytes)
            print(f"[CLIENT {c.client_id}] RTP decode SUCCESS")
        except Exception as e:
            print(f"[CLIENT {c.client_id}] RTP decode error: {e}")
            return

        curr_frame_nbr = rtp_packet.seqNum()
        print(f"[CLIENT {c.client_id}] RTP seqNum: {curr_frame_nbr}, current frame_nbr: {c.frame_nbr}")

        # --- actualizar estado de recepção e decidir NACK ---
        st = c.rtp_rx_state
        if st["last_seq"] is None:
            st["last_seq"] = curr_frame_nbr
            st["expected"] = 1
            st["received"] = 1
        else:
            delta = curr_frame_nbr - st["last_seq"]
            if delta > 0:
                st["expected"] += delta
                st["received"] += 1

                if delta > 1:
                    missing_first = st["last_seq"] + 1
                    missing_last = curr_frame_nbr - 1
                    loss_pct = (st["expected"] - st["received"]) / max(1, st["expected"])
                    print(
                        f"[CLIENT {c.client_id}] Link loss est={loss_pct*100:.2f}% "
                        f"(missing {missing_first}-{missing_last})"
                    )

                    if loss_pct >= c.LOSS_THRESHOLD and c.current_stream_id:
                        nack = NackPacket(c.current_stream_id, missing_first, missing_last)
                        try:
                            c.udp_sock.sendto(nack.serialize(), (remote_ip, UDP_PORT))
                            print(
                                f"[CLIENT {c.client_id}] NACK -> {remote_ip} "
                                f"stream={c.current_stream_id} seq=[{missing_first},{missing_last}]"
                            )
                        except OSError as e:
                            print(f"[CLIENT {c.client_id}] erro ao enviar NACK para {remote_ip}: {e}")

                st["last_seq"] = curr_frame_nbr
            else:
                # retransmitido/fora de ordem -> não mexemos nas stats
                pass

        # Discard late packets (out of order)
        with c.stream_lock:
            if curr_frame_nbr > c.frame_nbr:
                c.frame_nbr = curr_frame_nbr

                frame_data = rtp_packet.getPayload()
                self.write_frame(frame_data)

                if c.gui_root is not None:
                    try:
                        c.gui_root.after(0, self.update_video_frame)
                    except Exception as e:
                        print(f"[CLIENT {c.client_id}] Error scheduling GUI update: {e}")

    # ------------------------------------------------------------
    # Frame/cache helpers
    # ------------------------------------------------------------
    def write_frame(self, frame_data: bytes):
        c = self.client
        try:
            with open(c.cache_file, "wb") as f:
                f.write(frame_data)
        except Exception as e:
            print(f"[CLIENT {c.client_id}] Error writing frame: {e}")

    def update_video_frame(self):
        c = self.client
        try:
            if os.path.exists(c.cache_file) and c.video_label is not None:
                img = Image.open(c.cache_file)
                photo = ImageTk.PhotoImage(img)
                c.video_label.configure(image=photo)
                c.video_label.image = photo
        except Exception as e:
            print(f"[CLIENT {c.client_id}] GUI update error: {e}")
            pass

    # ------------------------------------------------------------
    # GUI legacy
    # ------------------------------------------------------------
    def start_gui(self):
        c = self.client
        try:
            c.gui_root = Tk()
            c.gui_root.title(f"Client {c.client_id} - Video Stream")

            c.video_label = Label(c.gui_root, height=600)
            c.video_label.pack(padx=5, pady=5)

            button_frame = Frame(c.gui_root)
            button_frame.pack(pady=5)

            play_btn = Button(button_frame, text="Play", width=15, command=self.play_stream)
            play_btn.pack(side=LEFT, padx=5)

            pause_btn = Button(button_frame, text="Pause", width=15, command=self.pause_stream)
            pause_btn.pack(side=LEFT, padx=5)

            stop_btn = Button(button_frame, text="Stop", width=15, command=self.stop_stream)
            stop_btn.pack(side=LEFT, padx=5)

            c.gui_root.protocol("WM_DELETE_WINDOW", self.on_gui_close)
            c.gui_root.mainloop()

        except Exception as e:
            print(f"[CLIENT {c.client_id}] Error starting GUI: {e}")

    # ------------------------------------------------------------
    # Player controls
    # ------------------------------------------------------------
    def play_stream(self):
        c = self.client
        if not c.current_stream_id:
            print("[CLIENT] No stream selected to play")
            return

        ack_ok, resp = c.net._send_stream_request(c.current_stream_id, RequestMethod.PLAY)
        if not ack_ok:
            return

        if resp is not None:
            print(f"[CLIENT {c.client_id}] RESPONSE PLAY status={resp.status} msg='{resp.message}'")

        with c.stream_lock:
            c.streaming_active = True

    def pause_stream(self):
        c = self.client
        if not c.current_stream_id:
            print("[CLIENT] No active stream to pause")
            return

        ack_ok, resp = c.net._send_stream_request(c.current_stream_id, RequestMethod.PAUSE)
        if not ack_ok:
            return

        if resp is not None:
            print(f"[CLIENT {c.client_id}] RESPONSE PAUSE status={resp.status} msg='{resp.message}'")

        with c.stream_lock:
            c.streaming_active = False

    def stop_stream(self):
        c = self.client
        if not c.current_stream_id:
            print("[CLIENT] No active stream to stop")
            return

        ack_ok, resp = c.net._send_stream_request(c.current_stream_id, RequestMethod.TEARDOWN)
        if not ack_ok:
            return

        if resp is not None:
            print(f"[CLIENT {c.client_id}] RESPONSE TEARDOWN status={resp.status} msg='{resp.message}'")

        with c.stream_lock:
            c.streaming_active = False
            c.current_stream_id = None
            c.frame_nbr = 0
            c.rtp_rx_state = {"last_seq": None, "expected": 0, "received": 0}

        if os.path.exists(c.cache_file):
            try:
                os.remove(c.cache_file)
            except Exception:
                pass

    def on_gui_close(self):
        c = self.client
        self.stop_stream()
        if c.gui_root:
            c.gui_root.destroy()
            c.gui_root = None
            c.video_label = None
