import tkinter as tk
import threading
# Importando as funções e variáveis dos seus novos arquivos:
from src.config import IP_SERVIDOR_BDO, PORTA_BDO, INTERVALO_MILISSEGUNDOS
from src.ping import disparar_ping

class PingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BDO Ping Overlay")
        self.root.overrideredirect(True)  # Remove bordas da janela
        self.root.attributes("-topmost", True)  # Sempre no topo do jogo

        # Windows Bugfix: Fundo ligeiramente diferente de puro preto (0,0,0)
        self.root.config(bg="#010101")
        self.root.attributes("-transparentcolor", "#010101")

        # Posição inicial na tela (X=1500, Y=50)
        self.root.geometry("+1500+50")

        # Controle de concorrência: garante que apenas UMA thread rode por vez
        self.thread_ativa = False

        # Texto do Ping
        self.label = tk.Label(
            self.root,
            text="BDO Ping: -- ms",
            font=("Consolas", 14, "bold"),
            fg="#00FF00",
            bg="#010101"
        )
        self.label.pack()

        # Arrastar a janela com o mouse
        self.label.bind("<Button-1>", self.iniciar_arrasto)
        self.label.bind("<B1-Motion>", self.arrastar_janela)

        # Inicia o ciclo de atualização seguro
        self.atualizar_ping_seguro()

    def iniciar_arrasto(self, event):
        self.x = event.x
        self.y = event.y

    def arrastar_janela(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        novo_x = self.root.winfo_x() + deltax
        novo_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{novo_x}+{novo_y}")

    def executar_ping_async(self):
        """Executa o teste de rede blindado e garante a liberação do estado"""
        try:
            tempo = disparar_ping(IP_SERVIDOR_BDO, PORTA_BDO)
            if self.root.winfo_exists():
                self.root.after(0, self.atualizar_interface, tempo)
        finally:
            self.thread_ativa = False

    def atualizar_interface(self, tempo):
        if tempo >= 0:
            texto = f"BDO Ping: {tempo} ms"
            if tempo < 40:
                cor = "#00FF00"  # Verde (Bom)
            elif tempo < 90:
                cor = "#FFFF00"  # Amarelo (Médio)
            else:
                cor = "#FF3333"  # Vermelho (Ruim)
        else:
            texto = "BDO Ping: FALHA"
            cor = "#FF3333"

        if self.root.winfo_exists():
            self.label.config(text=texto, fg=cor)

    def atualizar_ping_seguro(self):
        """Gerenciador de loop que impede o acúmulo de threads na memória"""
        if not self.thread_ativa:
            self.thread_ativa = True
            t = threading.Thread(target=self.executar_ping_async, daemon=True)
            t.start()

        if self.root.winfo_exists():
            self.root.after(INTERVALO_MILISSEGUNDOS, self.atualizar_ping_seguro)

    def iniciar(self):
        self.root.mainloop()
