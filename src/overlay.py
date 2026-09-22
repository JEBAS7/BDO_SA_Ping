import tkinter as tk
import threading
import win32gui
import win32process
import psutil
import sys
# Importando as funções e variáveis dos seus novos arquivos:
from src.config import IP_SERVIDOR_BDO, PORTA_BDO, INTERVALO_MILISSEGUNDOS
from src.ping import disparar_ping

# Nome do processo do jogo. Ajuste aqui se o executável tiver outro nome.
NOME_PROCESSO_JOGO = "BlackDesert64.exe"

# Intervalo (ms) para checar qual janela está em primeiro plano
INTERVALO_CHECAGEM_JANELA_MS = 300


def janela_ativa_e_do_jogo():
    """Retorna True se a janela em primeiro plano pertencer ao processo do jogo."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return False
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        nome_processo = psutil.Process(pid).name()
        return nome_processo.lower() == NOME_PROCESSO_JOGO.lower()
    except Exception:
        return False


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

        # CONTROLES DO MOUSE:
        # Clique com o botão esquerdo (Button-1) para arrastar
        self.label.bind("<Button-1>", self.iniciar_arrasto)
        self.label.bind("<B1-Motion>", self.arrastar_janela)

        # NOVO: Clique com o botão DIREITO (Button-3) para FECHAR o aplicativo
        self.label.bind("<Button-3>", self.fechar_aplicativo)

        # Controla se o overlay está atualmente visível
        self.overlay_visivel = True

        # Inicia o ciclo de atualização seguro
        self.atualizar_ping_seguro()

        # Inicia o ciclo que mostra/esconde o overlay conforme a janela ativa
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

    def checar_janela_ativa(self):
        """Mostra o overlay apenas quando o BDO está em primeiro plano."""
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
        """Fecha o overlay e encerra o processo do Python completamente."""
        if self.root.winfo_exists():
            self.root.destroy()
        sys.exit(0)

    def iniciar(self):
        self.root.mainloop()
