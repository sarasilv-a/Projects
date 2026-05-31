from tkinter import *
from PIL import Image, ImageTk
import os

CACHE_REFRESH_MS = 40  # ~25 fps

class ClientGUI:
    """
    GUI do cliente, inspirada no exemplo dos professores.
    Recebe um objeto Client (do client.py) e usa o cache_file
    que ele atualiza ao receber pacotes STREAM.
    """
    def __init__(self, master, client):
        self.master = master
        self.client = client

        self.master.protocol("WM_DELETE_WINDOW", self.handler)

        self.frame_nbr = 0
        self.update_job = None

        self.create_widgets()

        self.schedule_next_frame()

    # ---------------- GUI ----------------

    def create_widgets(self):
        """Cria widgets da janela."""
        # Label de vídeo
        self.label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)

        # Botão Play
        self.play_btn = Button(self.master, width=20, padx=3, pady=3)
        self.play_btn["text"] = "Play"
        self.play_btn["command"] = self.playMovie
        self.play_btn.grid(row=1, column=0, padx=2, pady=2)

        # Botão Pause
        self.pause_btn = Button(self.master, width=20, padx=3, pady=3)
        self.pause_btn["text"] = "Pause"
        self.pause_btn["command"] = self.pauseMovie
        self.pause_btn.grid(row=1, column=1, padx=2, pady=2)

        # Botão Stop/Teardown
        self.stop_btn = Button(self.master, width=20, padx=3, pady=3)
        self.stop_btn["text"] = "Teardown"
        self.stop_btn["command"] = self.exitClient
        self.stop_btn.grid(row=1, column=2, padx=2, pady=2)

    # ---------------- Handlers de botões ----------------

    def playMovie(self):
        self.client.play_stream()

    def pauseMovie(self):
        self.client.pause_stream()

    def exitClient(self):
        self.client.stop_stream()
        self.cancel_update_loop()
        self.master.destroy()

    # ---------------- Atualização de frame ----------------

    def schedule_next_frame(self):
        self.update_frame()
        self.update_job = self.master.after(CACHE_REFRESH_MS, self.schedule_next_frame)

    def cancel_update_loop(self):
        if self.update_job is not None:
            try:
                self.master.after_cancel(self.update_job)
            except Exception:
                pass
            self.update_job = None

    def update_frame(self):
        cache_file = self.client.cache_file
        try:
            if os.path.exists(cache_file):
                img = Image.open(cache_file)
                photo = ImageTk.PhotoImage(img)
                self.label.configure(image=photo, height=288)
                self.label.image = photo  # manter referência
        except Exception as e:
            print(f"[ClientGUI] erro a atualizar frame: {e}")

    # ---------------- Handler de fechar janela ----------------

    def handler(self):
        self.exitClient()
