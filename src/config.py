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
import psutil

# --- CONFIGURAÇÕES DO FPS ---
NOME_PROCESSO_EXE = "BlackDesert64.exe"
INTERVALO_FPS_MS = 500

# --- CONFIGURAÇÕES DE ATUALIZAÇÃO ---
INTERVALO_MILISSEGUNDOS = 1000

# Portas já confirmadas como prioritárias (ajuste aqui depois de rodar o
# diagnostico_conexoes_bdo.py e descobrir qual é a de gameplay de verdade)
PORTAS_GAMEPLAY_PRIORITARIAS = (8889,)


def obter_conexao_ativa_bdo():
    """Busca dinamicamente o IP ativo de gameplay com base nas faixas de portas do BDO"""
    ip_padrao, porta_padrao = "4.201.184.69", 8889

    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == NOME_PROCESSO_EXE:
            try:
                # Pegamos as conexões TCP ativas do processo
                conexoes = proc.connections(kind='tcp')

                # Procuramos pelas portas clássicas do jogo (faixas 8880-8890 e 9000-9010)
                for conn in conexoes:
                    if conn.status == 'ESTABLISHED':
                        porta_remota = conn.raddr.port

                        # Verifica se é uma das portas principais de gameplay mapeadas
                        if porta_remota in PORTAS_GAMEPLAY_PRIORITARIAS:
                            return conn.raddr.ip, porta_remota

                # Caso mude para uma porta secundária/nova dentro da faixa válida do jogo
                for conn in conexoes:
                    if conn.status == 'ESTABLISHED':
                        if (8880 <= conn.raddr.port <= 8890) or (9000 <= conn.raddr.port <= 9010):
                            return conn.raddr.ip, conn.raddr.port

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    return ip_padrao, porta_padrao


# --- CONFIGURAÇÕES DINÂMICAS ---
# O código agora varre as conexões de forma segura e puxa o IP correto automaticamente
IP_SERVIDOR_BDO, PORTA_BDO = obter_conexao_ativa_bdo()
