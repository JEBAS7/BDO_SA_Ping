import socket
import time

def disparar_ping(host, porta):
    timeout_segundos = 1.0  # Timeout curto para evitar acúmulo de threads
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout_segundos)
            antes = time.time()
            s.connect((host, porta))
            s.recv(32)  # Baixado para 32 bytes apenas para validar a resposta rápida
            depois = time.time()
            return int((depois - antes) * 1000)
    except Exception:
        # Captura qualquer erro de rede de forma genérica para não quebrar a thread
        return -1
