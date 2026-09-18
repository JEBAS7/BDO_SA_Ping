# BDO SA Ping Overlay 🎮📈

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/28e5a2c4-07fc-49ff-9df6-91f49547d2a6" />


Um utilitário leve e limpo desenvolvido em Python para monitorar a latência (ping) em tempo real diretamente na tela do jogo **Black Desert Online (Servidor SA)**. O programa cria uma sobreposição (overlay) transparente e móvel, permitindo que você acompanhe a estabilidade da sua conexão sem perder o foco na gameplay.

---

## ✨ Funcionalidades

* **Overlay Transparente:** Interface minimalista que remove as bordas do Windows e se integra ao jogo.
* **Sempre no Topo (Always on Top):** Garante que o contador de ping fique visível acima da janela do jogo.
* **Indicador Visual por Cor:**
  * 🟢 **Verde:** Conexão excelente (< 40ms)
  * 🟡 **Amarelo:** Conexão moderada (< 90ms)
  * 🔴 **Vermelho:** Latência alta ou Falha de conexão
* **Arrastável:** Clique e arraste o contador para qualquer lugar da tela com o mouse.
* **Assíncrono e Seguro:** Desenvolvido com multi-threading para garantir que os testes de rede não travem a sua tela.

---

## 📁 Estrutura do Projeto

O repositório segue as boas práticas de arquitetura modular em Python:

```text
BDO_SA_Ping/
├── assets/
│   ├── BDO.ico          # Recursos visuais (ícones e capturas de tela)
│   └── img.png          # Print da tela do Black Desert online com BDO ping
├── src/
│   ├── __init__.py      # Inicializador do pacote
│   ├── config.py        # Variáveis de ambiente e IPs dos servidores
│   ├── ping.py          # Lógica de comunicação de rede
│   ├── overlay.py       # Interface gráfica e loop assíncrono
│   └── main.py          # Ponto de entrada (Entrypoint) do programa
├── pyping.bat           # Inicializador rápido para Windows
└── README.md            # Documentação do projeto

```

---

## 🛠️ Como Configurar e Executar

### Pré-requisitos
* **Python 3.x** instalado no seu computador.

### Execução Rápida (Windows)
1. Baixe ou clone este repositório no seu computador.
2. Dê dois cliques no arquivo `pyping.bat` localizado na raiz do projeto. 
3. O overlay aparecerá na sua tela instantaneamente.

### Execução via Terminal
Caso prefira rodar manualmente pelo terminal ou prompt de comando na raiz do projeto:
```bash
python -m src.main
```

---

## ⚙️ Personalização

Se você quiser alterar o servidor de testes ou o tempo de atualização, basta abrir o arquivo `src/config.py` e modificar as variáveis:

```python
IP_SERVIDOR_BDO = "20.206.139.219"   # IP do servidor de destino
PORTA_BDO = 8884                     # Porta de comunicação
INTERVALO_MILISSEGUNDOS = 1000       # Tempo de espera entre cada checagem
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
