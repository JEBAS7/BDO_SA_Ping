"""
Medidor de FPS real do jogo, 100% em Python (sem PresentMon.exe).

Como funciona:
- Usa a biblioteca pywintrace para "escutar" os eventos do Windows (ETW) do
  provedor Microsoft-Windows-DXGI. Toda vez que o jogo apresenta um quadro na
  tela, o Windows emite o evento "Present_Start" (id 42) com o PID do processo.
- Contamos quantos desses eventos o BlackDesert64.exe gerou no último segundo.
- Nada é injetado dentro do jogo: só lemos o que o Windows já registra.

Sobre as telas de carregamento:
- Durante o carregamento o jogo apresenta milhares de quadros por segundo, mais
  do que o Python consegue processar (~450 eventos/s). Se o atraso passar de
  ~3 s, a sessão de captura é reiniciada (a fila velha é jogada fora).
- Valores acima de 1000 FPS são tratados como "sem valor" (é a tela de loading).

Sobre sessões ETW "esquecidas":
- Se o programa for encerrado à força (botão Stop do PyCharm), a sessão de
  captura fica aberta no Windows. O Windows aceita só 8 sessões por provedor;
  quando o limite é atingido, novas sessões não recebem evento nenhum.
  Por isso, ao iniciar, o programa fecha as sessões "BDO_FPS_*" antigas.

Requisitos:
- pip install pywintrace
- Executar o programa como ADMINISTRADOR (o Windows exige para criar a sessão).

Teste isolado (na pasta do projeto, como administrador):
    python -m src.fps
"""
import atexit
import inspect
import os
import subprocess
import threading
import time
from collections import deque


import psutil

try:
    import etw
    ETW_DISPONIVEL = True
except Exception:  # biblioteca não instalada
    ETW_DISPONIVEL = False

GUID_DXGI = "{CA11C036-0102-4A2D-A6AD-F03CFED5D3C9}"  # Microsoft-Windows-DXGI
ID_PRESENT_START = 42
PREFIXO_SESSAO = "BDO_FPS_"
SEGUNDOS_1601_ATE_1970 = 11644473600.0  # o TimeStamp do ETW é um FILETIME (desde 1601)
ATRASO_MAXIMO_S = 8.0          # eventos mais velhos que isso são descartados
LIMITE_REINICIO_S = 3.0        # atraso acima disso => reinicia a sessão de captura
INTERVALO_MIN_REINICIO_S = 3.0 # tempo mínimo entre dois reinícios
LIMITE_PARADA_S = 6.0          # sem NENHUM evento aceito por mais que isso => reinicia
                                # (cobre o caso do jogo rodando normal, mas o Windows
                                # parar de mandar Present_Start; o _atraso sozinho não
                                # detecta isso porque ele congela no último valor)
ESPERA_FILTRO_S = 8.0          # espera antes de concluir que o filtro/sessão não entrega nada
FPS_MAXIMO_VALIDO = 1000       # acima disso é tela de carregamento: não mostra
MSG_SEM_EVENTOS = "Nenhum evento recebido do Windows (sessões ETW antigas abertas?)"


class MedidorFPS:
    # O 1º parâmetro é ignorado (só existe para manter compatível com o overlay.py)
    def __init__(self, nome_processo_exe="BlackDesert64.exe"):
        self.nome_processo_exe = nome_processo_exe.lower()
        self.erro = None

        self._quadros = deque()   # timestamps (segundos) dos últimos quadros
        self._lock = threading.Lock()
        self._pids = set()
        self._rodando = False
        self._job = None
        self._geracao = 0         # identifica a sessão atual (eventos de sessões velhas são ignorados)
        self._nome_sessao = None
        self._limpeza_tentada = False
        self._ultimo_evento = 0.0
        self._atraso = 0.0        # quanto o Python está atrasado em relação ao Windows

        # Informações de diagnóstico
        self.modo = "filtro"      # "filtro" (rápido) ou "sem_filtro" (mais pesado)
        self.reinicios = 0
        self.parametros_usados = {}
        self.ultima_excecao = None
        self._inicio_sessao = 0.0
        self._ultimo_reinicio = 0.0
        self._cont = self._zerar_contadores()

    @staticmethod
    def _zerar_contadores():
        return {"recebidos": 0, "do_jogo": 0, "atrasados": 0, "excecoes": 0}

    # ------------------------------------------------------------------ API
    def iniciar(self):
        if not ETW_DISPONIVEL:
            self.erro = "pywintrace não instalado (pip install pywintrace)"
            print("[FPS]", self.erro)
            return
        self._rodando = True
        atexit.register(self.parar)  # fecha a sessão ETW se o programa terminar normalmente
        atexit.register(self._cleanup_etw)  # cleanup extra caso o app seja morto abruptamente
        threading.Thread(target=self._loop, daemon=True).start()

    def parar(self):
        """Para a sessão ETW explicitamente."""
        try:
            if self._nome_sessao:
                subprocess.run(
                    ["logman", "stop", self._nome_sessao, "-ets"],
                    capture_output=True, timeout=5
                )
        except Exception:
            pass
        self._rodando = False
        self._geracao += 1
        job, self._job = self._job, None
        self._parar_job(job)

    def _cleanup_etw(self):
        """Cleanup de emergência — roda mesmo se o app for morto abruptamente."""
        try:
            if self._nome_sessao:
                subprocess.run(
                    ["logman", "stop", self._nome_sessao, "-ets"],
                    capture_output=True, timeout=3
                )
        except Exception:
            pass

    def valor(self):
        """FPS atual (int) ou None se o jogo não está enviando quadros."""
        with self._lock:
            if len(self._quadros) < 2:
                return None
            if (time.time() - self._ultimo_evento) > 4.0:
                return None
            intervalo = self._quadros[-1] - self._quadros[0]
            if intervalo <= 0:
                return None
            fps = int(round((len(self._quadros) - 1) / intervalo))
            return fps if fps <= FPS_MAXIMO_VALIDO else None

    def sem_evento_ha(self):
        """Segundos desde o último quadro do jogo aceito."""
        return time.time() - self._ultimo_evento if self._ultimo_evento else -1.0

    def atraso(self):
        """Atraso (em segundos) entre o Windows gerar o evento e o Python processar."""
        return self._atraso

    # ------------------------------------------------------------- interno
    @staticmethod
    def _parar_job(job):
        if job is not None:
            try:
                job.stop()
            except Exception:
                pass

    @staticmethod
    def _limpar_sessoes_antigas(manter=None):
        """Fecha sessões ETW 'BDO_FPS_*' que ficaram abertas de execuções anteriores."""
        try:
            saida = subprocess.run(
                ["logman", "query", "-ets"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore",
                creationflags=subprocess.CREATE_NO_WINDOW, timeout=20,
            ).stdout
        except Exception:
            return
        for linha in saida.splitlines():
            partes = linha.split()
            if not partes or not partes[0].startswith(PREFIXO_SESSAO) or partes[0] == manter:
                continue
            try:
                subprocess.run(
                    ["logman", "stop", partes[0], "-ets"],
                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=20,
                )
                print(f"[FPS] Sessão ETW antiga fechada: {partes[0]}")
            except Exception:
                pass

    def _criar_job(self, usar_filtro):
        geracao = self._geracao

        def callback(x):
            # Ignora eventos que chegam de uma sessão que já foi substituída
            if geracao == self._geracao:
                self._ao_receber_evento(x)

        provedores = [etw.ProviderInfo("Microsoft-Windows-DXGI", etw.GUID(GUID_DXGI))]
        kwargs = {"providers": provedores, "event_callback": callback}

        # Só passa os parâmetros que a versão instalada do pywintrace aceita.
        aceitos = inspect.signature(etw.ETW.__init__).parameters

        if usar_filtro and "event_id_filters" in aceitos:
            # Ignora os outros ~10 eventos por quadro (só gastavam processamento).
            kwargs["event_id_filters"] = [ID_PRESENT_START]
        if "session_name" in aceitos:
            # Nome único por sessão, para uma nova poder subir antes da velha terminar de parar
            self._nome_sessao = f"{PREFIXO_SESSAO}{os.getpid()}_{geracao}"
            kwargs["session_name"] = self._nome_sessao

        self.parametros_usados = {k: v for k, v in kwargs.items() if k not in ("providers", "event_callback")}
        return etw.ETW(**kwargs)

    def _iniciar_sessao(self, usar_filtro):
        self.modo = "filtro" if usar_filtro else "sem_filtro"
        self._cont = self._zerar_contadores()
        self._job = self._criar_job(usar_filtro)
        self._job.start()
        self._inicio_sessao = time.time()

    def _reiniciar_sessao(self):
        """Joga fora a fila atrasada: para a sessão velha (sem esperar) e abre uma nova."""
        self._ultimo_reinicio = time.time()
        self.reinicios += 1
        self._geracao += 1
        velho, self._job = self._job, None
        if velho is not None:
            threading.Thread(target=self._parar_job, args=(velho,), daemon=True).start()
        with self._lock:
            self._quadros.clear()
        self._atraso = 0.0
        try:
            self._iniciar_sessao(usar_filtro=(self.modo == "filtro"))
        except Exception as e:
            print(f"[FPS] Falha ao reiniciar a sessão ETW: {e}")

    def _loop(self):
        # Fecha sessões que ficaram abertas quando o programa anterior foi encerrado à força
        self._limpar_sessoes_antigas()
        try:
            self._iniciar_sessao(usar_filtro=True)
        except Exception as e:
            self.erro = f"Falha ao iniciar ETW (está como administrador?): {e}"
            print("[FPS]", self.erro)
            return

        ultima_checagem_pids = 0.0
        while self._rodando:
            agora = time.time()
            if agora - ultima_checagem_pids >= 3.0:
                ultima_checagem_pids = agora
                self._atualizar_pids()   # o jogo pode ser reaberto
                self._vigiar_sessao()
            self._vigiar_atraso()
            self._vigiar_parada()
            time.sleep(0.5)

    def _vigiar_atraso(self):
        """Se o Python ficou muito atrasado em relação ao Windows, reinicia a captura."""
        if self._atraso > LIMITE_REINICIO_S and (time.time() - self._ultimo_reinicio) > INTERVALO_MIN_REINICIO_S:
            print(f"[FPS] Fila atrasada ({self._atraso:.1f}s); reiniciando a captura.")
            self._reiniciar_sessao()

    def _vigiar_parada(self):
        """Detecta o caso em que a captura para de receber eventos NO MEIO do jogo
        (jogo rodando normal, não é tela de loading). Diferente de _vigiar_atraso
        (que depende de _atraso subir) e de _vigiar_sessao (que olha contadores
        acumulados desde o início da sessão e por isso nunca volta a "zero"
        depois do primeiro evento), aqui olhamos direto o tempo desde o ÚLTIMO
        evento aceito do jogo. É o mesmo valor que faz valor() cair para None
        (o "--" cinza no overlay) — então, se ficou tempo demais assim, força
        um reinício da sessão em vez de deixar cinza para sempre.
        """
        if not self._pids or not self._ultimo_evento:
            return
        parado_ha = time.time() - self._ultimo_evento
        if parado_ha > LIMITE_PARADA_S and (time.time() - self._ultimo_reinicio) > INTERVALO_MIN_REINICIO_S:
            print(f"[FPS] Sem eventos do jogo há {parado_ha:.1f}s; reiniciando a captura.")
            self._reiniciar_sessao()

    def _vigiar_sessao(self):
        """Detecta sessão ETW 'morta' (sem evento nenhum) e tenta se curar sozinha.

        Isso cobre o caso de o app anterior ter sido morto pelo Gerenciador de
        Tarefas: a sessão órfã fica segurando o limite de 8 sessões por
        provedor, e a sessão nova (mesmo no modo "filtro") não recebe nenhum
        evento. Antes de trocar de modo, tentamos limpar sessões órfãs e
        reiniciar — isso resolve o caso sem precisar rodar 'logman' na mão.
        """
        if not self._pids or (time.time() - self._inicio_sessao) < ESPERA_FILTRO_S:
            return

        if self.modo == "filtro":
            sem_eventos = self._cont["do_jogo"] == 0 and self._cont["atrasados"] == 0
        else:
            # Modo sem filtro: o jogo gera ~11 eventos por quadro. Se não chegou
            # NADA, a sessão está morta.
            sem_eventos = self._cont["recebidos"] == 0

        if not sem_eventos:
            if self.erro == MSG_SEM_EVENTOS:
                self.erro = None  # voltou a receber eventos
            return

        if not self._limpeza_tentada:
            # 1ª tentativa, em qualquer modo: pode ser sessão órfã de uma
            # execução anterior encerrada à força. Limpa e reinicia no mesmo modo.
            self._limpeza_tentada = True
            print(f"[FPS] Sem eventos no modo '{self.modo}'; fechando sessões ETW "
                  f"antigas e tentando de novo.")
            self._limpar_sessoes_antigas(manter=self._nome_sessao)
            self._reiniciar_sessao()
            return

        if self.modo == "filtro":
            # A limpeza não resolveu: tenta sem filtro (pode ser questão de
            # compatibilidade do filtro nessa versão do pywintrace/Windows).
            print("[FPS] Ainda sem eventos do jogo com filtro; tentando sem filtro.")
            self._limpeza_tentada = False  # permite tentar limpar de novo no modo sem_filtro
            self._geracao += 1
            velho, self._job = self._job, None
            self._parar_job(velho)
            try:
                self._iniciar_sessao(usar_filtro=False)
            except Exception as e:
                self.erro = f"Falha ao reiniciar ETW: {e}"
                print("[FPS]", self.erro)
            return

        # Já tentamos limpar e trocar de modo; não tem mais o que fazer sozinho.
        if not self.erro:
            self.erro = MSG_SEM_EVENTOS
            print("[FPS]", self.erro, "- reinicie o Windows ou feche as sessões com 'logman'.")

    def _atualizar_pids(self):
        pids = set()
        for p in psutil.process_iter(["pid", "name"]):
            nome = (p.info.get("name") or "").lower()
            if nome == self.nome_processo_exe:
                pids.add(p.info["pid"])
        self._pids = pids

    def _ao_receber_evento(self, x):
        self._cont["recebidos"] += 1
        try:
            id_evento, dados = x[0], x[1]
            if id_evento != ID_PRESENT_START:
                return
            cabecalho = dados.get("EventHeader", {})
            if cabecalho.get("ProcessId") not in self._pids:
                return
            self._cont["do_jogo"] += 1

            ts = cabecalho.get("TimeStamp")
            if isinstance(ts, int) and ts > 0:
                momento = ts / 1e7  # segundos desde 1601
                atraso = (time.time() + SEGUNDOS_1601_ATE_1970) - momento
                self._atraso = atraso
                # Fila muito atrasada: o número seria de muito tempo atrás.
                if atraso > ATRASO_MAXIMO_S:
                    self._cont["atrasados"] += 1
                    with self._lock:
                        self._quadros.clear()
                    return
            else:
                momento = time.perf_counter()
        except Exception as e:
            self._cont["excecoes"] += 1
            self.ultima_excecao = repr(e)
            return

        with self._lock:
            self._quadros.append(momento)
            self._ultimo_evento = time.time()
            # Mantém só ~1 segundo de histórico
            while self._quadros and (momento - self._quadros[0]) > 1.0:
                self._quadros.popleft()


if __name__ == "__main__":
    try:
        from importlib.metadata import version
        print("pywintrace versão:", version("pywintrace"))
    except Exception:
        print("pywintrace versão: desconhecida")

    m = MedidorFPS()
    m.iniciar()
    time.sleep(1)
    print("Parâmetros usados:", m.parametros_usados)
    print("Teste de 120 segundos. Troque de cena no jogo (cidade <-> barco) durante o teste.")
    for _ in range(120):
        time.sleep(1)
        c = m._cont
        print(f"FPS: {m.valor()} | atraso: {m.atraso():.1f}s | sem evento há: {m.sem_evento_ha():.1f}s | "
              f"reinícios: {m.reinicios} | recebidos: {c['recebidos']} do_jogo: {c['do_jogo']} | "
              f"PIDs: {m._pids} | modo: {m.modo} | erro: {m.erro}")
    m.parar()
