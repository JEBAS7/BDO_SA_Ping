"""
Diagnóstico de conexões do BDO
--------------------------------
Esse script fica monitorando, por um tempo, todas as conexões TCP
ESTABLISHED do processo BlackDesert64.exe dentro das faixas de porta
"clássicas" de gameplay (8880-8890 e 9000-9010), e mostra qual delas
se mantém mais tempo ativa continuamente.

A ideia: a conexão de gameplay de verdade tende a ficar ESTABLISHED
o tempo inteiro enquanto você joga. Conexões auxiliares (mercado
central, chat, canal secundário etc.) tendem a aparecer e sumir,
ou ficar pouco tempo abertas.

Como usar:
1. Abra o BDO e entre no jogo (ou fique andando/lutando).
2. Rode este script: python diagnostico_conexoes_bdo.py
3. Deixe rodando por 30-60 segundos.
4. Aperte Ctrl+C para ver o resumo final.
"""

import time
import psutil

NOME_PROCESSO_EXE = "BlackDesert64.exe"
INTERVALO_AMOSTRA_S = 1.0

FAIXAS_GAMEPLAY = [
    (8880, 8890),
    (9000, 9010),
]


def porta_e_gameplay(porta: int) -> bool:
    return any(inicio <= porta <= fim for inicio, fim in FAIXAS_GAMEPLAY)


def conexoes_candidatas():
    """Retorna lista de (ip, porta) ESTABLISHED do BDO nas faixas de gameplay."""
    candidatas = []
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] != NOME_PROCESSO_EXE:
            continue
        try:
            for conn in proc.connections(kind='tcp'):
                if conn.status == 'ESTABLISHED' and conn.raddr and porta_e_gameplay(conn.raddr.port):
                    candidatas.append((conn.raddr.ip, conn.raddr.port))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return candidatas


def main():
    # streak atual (amostras consecutivas vendo essa conexão)
    streak_atual = {}
    # maior streak já visto para essa conexão
    maior_streak = {}
    # quantas amostras no total essa conexão apareceu
    total_amostras = {}

    print("Monitorando conexões do BDO... (Ctrl+C para parar e ver o resumo)\n")

    try:
        while True:
            vistas_agora = set(conexoes_candidatas())

            for chave in vistas_agora:
                streak_atual[chave] = streak_atual.get(chave, 0) + 1
                total_amostras[chave] = total_amostras.get(chave, 0) + 1
                maior_streak[chave] = max(maior_streak.get(chave, 0), streak_atual[chave])

            # zera o streak de quem sumiu nessa rodada
            for chave in list(streak_atual.keys()):
                if chave not in vistas_agora:
                    streak_atual[chave] = 0

            linha = "  ".join(
                f"{ip}:{porta} (streak={streak_atual[(ip, porta)]}s)"
                for ip, porta in vistas_agora
            ) or "(nenhuma conexão de gameplay encontrada agora)"
            print(linha)

            time.sleep(INTERVALO_AMOSTRA_S)

    except KeyboardInterrupt:
        print("\n\n=== RESUMO ===")
        if not total_amostras:
            print("Nenhuma conexão foi vista. O jogo estava aberto durante o teste?")
            return

        ranking = sorted(
            total_amostras.keys(),
            key=lambda k: (maior_streak[k], total_amostras[k]),
            reverse=True,
        )
        for ip, porta in ranking:
            print(
                f"{ip}:{porta}  ->  visto em {total_amostras[(ip, porta)]} amostras, "
                f"streak contínuo máximo de {maior_streak[(ip, porta)]}s"
            )

        melhor = ranking[0]
        print(
            f"\nCandidata mais provável a ser a conexão de gameplay: "
            f"{melhor[0]}:{melhor[1]}"
        )
        print(
            "(a que ficou continuamente ESTABLISHED por mais tempo, sem cair)"
        )


if __name__ == "__main__":
    main()
