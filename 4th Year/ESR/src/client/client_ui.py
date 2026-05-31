from tkinter import Tk
from protocols.stream_request_packet import RequestMethod


class ClientUI:
    def __init__(self, client):
        self.client = client

    def show_neighbors(self):
        c = self.client
        print("\n=== Vizinhos do cliente ===")
        print(f"- Vizinho principal: {c.neighbor_ip} (ctrl_port={c.CTRL_PORT})")
        print("===========================\n")

    def menu_loop(self):
        c = self.client
        while True:
            print("===== MENU CLIENTE =====")
            print("1 - Ver vídeo")
            print("2 - Ver vizinhos")
            print("3 - Sair da rede")
            print("4 - Listar streams disponíveis no nó")
            print("========================")

            choice = input("Escolha uma opção: ").strip()

            if choice == "1":
                self.show_video_menu()
            elif choice == "2":
                self.show_neighbors()
            elif choice == "3":
                print("[CLIENT] A sair da rede...")
                c.leave_network()
                print("[CLIENT] Adeus.")
                break
            elif choice == "4":
                c.request_stream_list()
            else:
                print("Opção inválida.\n")

    def request_stream(self):
        c = self.client
        stream_id = input("ID da stream que queres ver: ").strip()
        if not stream_id:
            print("Stream ID vazio, a cancelar.\n")
            return False

        ack_ok, resp = c.net._send_stream_request(stream_id, RequestMethod.PLAY)

        if not ack_ok:
            print(f"[CLIENT {c.client_id}] REQUEST PLAY não foi confirmado por ACK.\n")
            return False

        if resp is None:
            print("[CLIENT] não recebeu resposta ao pedido de stream.\n")
            return False

        print(
            f"[CLIENT {c.client_id}] RESPONSE para req_id={resp.req_id} "
            f"status={resp.status} msg='{resp.message}'"
        )

        if resp.status == 0:
            print("[CLIENT] pedido de stream aceite (PLAY OK).")
            with c.stream_lock:
                c.current_stream_id = stream_id
                c.streaming_active = True
                c.frame_nbr = 0
                c.rtp_rx_state = {"last_seq": None, "expected": 0, "received": 0}

            print("[CLIENT] A receber stream... (a GUI vai abrir)\n")
            return True

        print("[CLIENT] pedido de stream recusado/erro.\n")
        return False

    def show_video_menu(self):
        ok = self.request_stream()
        if not ok:
            return

        # GUI "dos profs": usa o ClientGUI que lê cache_file do Client
        from client_gui import ClientGUI

        root = Tk()
        root.title(f"Cliente {self.client.client_id} - Video Stream")

        app = ClientGUI(root, self.client)
        app.master.title(f"Cliente {self.client.client_id}")

        root.mainloop()
