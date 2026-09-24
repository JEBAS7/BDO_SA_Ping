import tkinter as tk
import threading
import win32gui
import win32process
import psutil
import sys

from src.config import (
    IP_SERVIDOR_BDO, PORTA_BDO, INTERVALO_MILISSEGUNDOS,
    NOME_PROCESSO_EXE, INTERVALO_FPS_MS,
)
from src.ping import disparar_ping
from src.fps import MedidorFPS

NOME_PROCESSO_JOGO = "BlackDesert64"
INTERVALO_CHECAGEM_JANELA_MS = 300


def janela_ativa_e_do_jogo():
    """Retorna True se a janela em primeiro plano pertencer ao processo do jogo."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return False
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        nome_processo = psutil.Process(pid).name()
        return NOME_PROCESSO_JOGO.lower() in nome_processo.lower()
    except Exception:
        return False


class PingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BDO Ping Overlay")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Configurações de Transparência completas e sólidas para o Windows
        self.root.config(bg="#010101")
        self.root.attributes("-transparentcolor", "#010101")

        self.root.geometry("260x65+1500+50")

        self.thread_ativa = False
        self.ping_atual = "--"
        self.cor_texto = "#00FF00"

        # Medidor de FPS real (PresentMon)
        self.medidor_fps = MedidorFPS(nome_processo_exe=NOME_PROCESSO_EXE)
        self.medidor_fps.iniciar()

        # LINHA 1: Label do BDO Ping
        self.label_ping = tk.Label(
            self.root,
            text="BDO Ping: -- ms",
            font=("Consolas", 14, "bold"),
            fg=self.cor_texto,
            bg="#010101",
            anchor="w"
        )
        self.label_ping.pack(fill="x", padx=10, pady=(5, 0))

        # LINHA 2: Label do FPS diretamente abaixo
        self.label_fps = tk.Label(
            self.root,
            text="FPS: --",
            font=("Consolas", 14, "bold"),
            fg=self.cor_texto,
            bg="#010101",
            anchor="w"
        )
        self.label_fps.pack(fill="x", padx=10, pady=(2, 0))

        # Controles de arrastar e fechar nas duas linhas
        for label in (self.label_ping, self.label_fps):
            label.bind("<Button-1>", self.iniciar_arrasto)
            label.bind("<B1-Motion>", self.arrastar_janela)
            label.bind("<Button-3>", self.fechar_aplicativo)

        self.overlay_visivel = True

        # Inicializa as rotinas em segundo plano
        self.atualizar_ping_seguro()
        self.atualizar_fps()
        self.checar_janela_ativa()

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
        try:
            tempo = disparar_ping(IP_SERVIDOR_BDO, PORTA_BDO)
            if self.root.winfo_exists():
                self.root.after(0, self.atualizar_interface_ping, tempo)
        finally:
            self.thread_ativa = False

    def atualizar_interface_ping(self, tempo):
        if tempo >= 0:
            self.ping_atual = f"{tempo} ms"
            if tempo < 40:
                self.cor_texto = "#00FF00"
            elif tempo < 90:
                self.cor_texto = "#FFFF00"
            else:
                self.cor_texto = "#FF3333"
        else:
            self.ping_atual = "FALHA"
            self.cor_texto = "#FF3333"

        self.label_ping.config(text=f"BDO Ping: {self.ping_atual}", fg=self.cor_texto)

    def atualizar_fps(self):
        """Lê o FPS real medido pelo PresentMon e mostra na tela."""
        if not self.root.winfo_exists():
            return

        cor = "#AAAAAA"  # cinza quando não há valor
        if self.medidor_fps.erro:
            texto = "FPS: N/D"
            cor = "#FF3333"   # vermelho: problema na captura
        else:
            valor = self.medidor_fps.valor()
            if valor is None:
                texto = "FPS: --"
            else:
                texto = f"FPS: {valor}"
                if valor >= 60:
                    cor = "#00FF00"   # verde
                elif valor >= 20:
                    cor = "#FFFF00"   # amarelo
                else:
                    cor = "#FF3333"   # vermelho

        self.label_fps.config(text=texto, fg=cor)
        self.root.after(INTERVALO_FPS_MS, self.atualizar_fps)

    def atualizar_ping_seguro(self):
        if not self.thread_ativa:
            self.thread_ativa = True
            t = threading.Thread(target=self.executar_ping_async, daemon=True)
            t.start()
        if self.root.winfo_exists():
            self.root.after(INTERVALO_MILISSEGUNDOS, self.atualizar_ping_seguro)

    def checar_janela_ativa(self):
        if not self.root.winfo_exists():
            return
        deve_mostrar = janela_ativa_e_do_jogo()

        if deve_mostrar and not self.overlay_visivel:
            self.root.deiconify()
            self.overlay_visivel = True
        elif not deve_mostrar and self.overlay_visivel:
            self.root.withdraw()
            self.overlay_visivel = False
        self.root.after(INTERVALO_CHECAGEM_JANELA_MS, self.checar_janela_ativa)

    def fechar_aplicativo(self, event=None):
        self.medidor_fps.parar()  # encerra o PresentMon junto
        if self.root.winfo_exists():
            self.root.destroy()
        sys.exit(0)

    def iniciar(self):
        try:
            self.root.mainloop()
        finally:
            self.medidor_fps.parar()
