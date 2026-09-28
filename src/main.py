'''Copyright 2026 JEBAS7

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''

import tkinter as tk
from tkinter import messagebox
import sys
import ctypes
from ctypes import wintypes

# ---------- Single Instance via Mutex ----------

def ja_esta_rodando() -> bool:
    """
    Retorna True se já existe outra instância do app em execução.
    Usa um mutex nomeado do Windows (Liberado automaticamente quando o processo morre).
    """
    nome_mutex = "Local\\BDO_SA_Ping_SingleInstance_Mutex_v1"
    ERROR_ALREADY_EXISTS = 183

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [wintypes.LPCVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE

    handle = kernel32.CreateMutexW(None, False, nome_mutex)
    erro = ctypes.get_last_error()

    if erro == ERROR_ALREADY_EXISTS:
        if handle:
            kernel32.CloseHandle(handle)
        return True

    # Guarda o handle numa referência global pra não ser coletado pelo GC
    global _mutex_handle
    _mutex_handle = handle
    return False

# ---------- Main ----------

def main():
    # 1. Checa se já tem instância rodando ANTES de qualquer coisa
    if ja_esta_rodando():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "BDO SA Ping",
            "O BDO SA Ping já está em execução.\n\n"
            "Procure o overlay na tela ou feche a instância atual\n"
            "antes de abrir outra."
        )
        root.destroy()
        sys.exit(0)

    # 2. Só então inicia o overlay
    from src.overlay import PingOverlay
    overlay = PingOverlay()
    overlay.iniciar()


if __name__ == "__main__":
    main()