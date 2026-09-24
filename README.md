# BDO SA Ping Overlay 🎮📈

Um utilitário leve e limpo desenvolvido em Python para monitorar a latência (ping) e FPS em tempo real diretamente na tela do jogo **Black Desert Online (Servidor SA)**. O programa cria uma sobreposição (overlay) transparente e móvel, permitindo que você acompanhe a estabilidade da sua conexão sem perder o foco na gameplay.

---

## 🛠️ Por que este projeto foi criado?

Como jogador de BDO, senti muita falta de um monitor de ping e FPS nativo dentro do jogo. Após sugerir essa implementação para a Pearl Abyss diversas vezes e não obter retorno, decidi criar uma solução própria, leve e focada na comunidade do servidor SA.

## ⚔️ Benefícios no Jogo

- **Evite mortes em spots:** Monitore sua conexão em tempo real enquanto faz o seu grind e evite surpresas com picos de lag que podem destruir seus cristais.
- **Navegação segura:** Não perca o seu barco de vista por causa de dessincronização com o servidor, evitando ter que nadar longas distâncias para alcançá-lo.
- **Leve e Seguro:** Desenvolvido para não impactar o FPS do seu jogo. Não injeta código, não lê a memória do jogo e não interage com o processo do BDO — apenas usa APIs nativas do Windows (ETW/DXGI) para FPS e sockets UDP/TCP para medir latência, da mesma forma que ferramentas como Discord e Steam.

## ✨ Funcionalidades

- **Overlay Transparente:** Interface minimalista que remove as bordas do Windows e se integra ao jogo.
- **Sempre no Topo (Always on Top):** Garante que o contador de ping fique visível acima da janela do jogo.
- **Indicador Visual por Cor:**

  **Ping**
  - 🟢 **Verde:** Conexão excelente (< 40ms)
  - 🟡 **Amarelo:** Conexão moderada (< 90ms)
  - 🔴 **Vermelho:** Latência alta ou falha de conexão

  **FPS**
  - 🟢 **Verde:** FPS Bom (> 60 FPS)
  - 🟡 **Amarelo:** FPS Razoável (entre 59 FPS e 20 FPS)
  - 🔴 **Vermelho:** FPS Ruim (< 20 FPS)
  - ⚪ **Cinza:** FPS -- (> 1000 FPS ou falha)

- **Arrastável:** Clique e arraste o contador para qualquer lugar da tela com o mouse.
- **Assíncrono e Seguro:** Desenvolvido com multi-threading para garantir que os testes de rede não travem a sua tela.

---

## 🛡️ Não é um cheat — como funciona

Este projeto é um **monitor externo**, não um cheat. Ele **não interage** com o cliente do Black Desert Online de nenhuma forma ativa.

### O que ele faz

- **Ping:** mede latência via `socket` puro (UDP/TCP) até o servidor SA — exatamente como o comando `ping` do Windows.
- **FPS:** obtém contadores via **ETW (Event Tracing for Windows)** no provedor público `Microsoft-Windows-DXGI`. É o próprio Windows reportando quantos frames foram apresentados por segundo, via `pywintrace`. Nenhum hook em DirectX, nenhuma injeção.
- **Detecção de jogo ativo:** usa `win32gui` + `psutil` apenas para verificar se o processo `BlackDesert64` está em primeiro plano — nada é lido ou escrito nele.
- **Interface:** overlay Tkinter transparente, sempre no topo. Uma janela comum do Windows, como Discord ou Steam.

### O que ele NÃO faz

- ❌ Não usa `ReadProcessMemory` / `WriteProcessMemory`
- ❌ Não usa `CreateRemoteThread` / injeção de DLL
- ❌ Não usa `SetWindowsHookEx` (nem de teclado, nem de mouse)
- ❌ Não faz hook em DirectX / DXGI / OpenGL
- ❌ Não abre handle no processo do jogo (`OpenProcess`)
- ❌ Não registra hotkeys globais — a interação é só com clique direito (fechar) e arraste (mover) na própria janela

### Assinatura

O executável é assinado digitalmente com certificado **self-signed** (Authenticode), por ser um projeto gratuito e sem fins lucrativos. O Windows SmartScreen pode exibir um alerta na primeira execução — clique em "Mais informações" → "Executar assim mesmo". O código é 100% aberto e auditável neste repositório.

---

## 📁 Estrutura do Projeto

O repositório segue as boas práticas de arquitetura modular em Python:

```
BDO_SA_Ping/
├── assets/
│   ├── BDO.ico          # Recursos visuais (ícones e capturas de tela)
│   └── img.png          # Print da tela do Black Desert Online com BDO Ping
├── src/
│   ├── __init__.py      # Inicializador do pacote
│   ├── config.py        # Variáveis de ambiente e IPs dos servidores
│   ├── fps.py           # pywintrace para "escutar" os eventos do Windows (ETW) do provedor Microsoft-Windows-DXGI (monitor de FPS)
│   ├── ping.py          # Lógica de comunicação de rede
│   ├── overlay.py       # Interface gráfica e loop assíncrono
│   └── main.py          # Ponto de entrada (Entrypoint) do programa
├── pyping.bat           # Inicializador rápido para Windows
└── README.md            # Documentação do projeto
```

---

## 🛠️ Como Configurar e Executar

### Pré-requisitos

- **Python 3.x** instalado no seu computador.

### Execução Rápida (Windows)

1. Baixe ou clone este repositório no seu computador.
2. Dê dois cliques no arquivo `pyping.bat` localizado na raiz do projeto.
3. O overlay aparecerá na sua tela instantaneamente.

### Fechar aplicativo

Caso queira fechar a aplicação, basta clicar com o **botão direito do mouse** em cima do BDO Ping.

### Execução via Terminal

Caso prefira rodar manualmente pelo terminal ou prompt de comando na raiz do projeto:

```
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

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.