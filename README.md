# BDO SA Ping Overlay 🎮📈

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1d9a682d-b0f6-4bcb-a177-4567bcc51e0c" />

Um utilitário leve e limpo desenvolvido em Python para monitorar a latência (ping) e FPS em tempo real diretamente na tela do jogo **Black Desert Online (Servidor SA)**. O programa cria uma sobreposição (overlay) transparente e móvel, permitindo que você acompanhe a estabilidade da sua conexão sem perder o foco na gameplay.

---

## 🛠️ Por que este projeto foi criado?

Como jogador de BDO, senti muita falta de um monitor de ping e FPS nativo dentro do jogo. Após sugerir essa implementação para a Pearl Abyss diversas vezes e não obter retorno, decidi criar uma solução própria, leve e focada na comunidade do servidor SA.

## ⚔️ Benefícios no Jogo

- **Evite mortes em spots:** Monitore sua conexão em tempo real enquanto faz o seu grind e evite surpresas com picos de lag que podem destruir seus cristais.
- **Navegação segura:** Não perca o seu barco de vista por causa de dessincronização com o servidor, evitando ter que nadar longas distâncias para alcançá-lo.
- **Leve e Seguro:** Desenvolvido para não impactar o FPS do seu jogo. Não injeta código, não lê a memória do jogo e não interage com o processo do BDO — apenas usa APIs nativas do Windows (ETW/DXGI) para FPS e sockets UDP/TCP para medir latência, da mesma forma que ferramentas como Discord e Steam.

## ✨ Funcionalidades

- **Detecção Dinâmica de Servidor:** Identifica automaticamente o IP e a porta de gameplay activa do BDO, adaptando-se instantaneamente quando você troca de canal (ex: Balenos, Serendia, Temporada) sem quebrar o monitoramento ou precisar reiniciar o script.
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
  - 🟢 **Verde, "999" fixo:** captura se autocorrigindo internamente (reinício rápido de sessão durante loadings/transições) — não é uma leitura real, só evita mostrar "--" piscando nesse meio-tempo
  - ⚪ **Cinza:** FPS -- indica falha real de captura (jogo fechado ou sem conseguir se recuperar)

- **Arrastável:** Clique e arraste o contador para qualquer lugar da tela com o mouse.
- **Assíncrono e Seguro:** Desenvolvido com multi-threading para garantir que os testes de rede não travem a sua tela.

---

## Limitações conhecidas

O overlay não aparece em modo Tela Cheia (exclusiva), pois esse modo faz o jogo assumir controle direto da GPU, ignorando o compositor do Windows (DWM) — nenhuma janela externa consegue desenhar por cima nesse caso. A captura de ping/FPS continua rodando normalmente por trás.
Use Tela Cheia em Janela (borderless) para o overlay aparecer normalmente.

## 🛡️ Não é um cheat — como funciona

Este projeto é um **monitor externo**, não um cheat. Ele **não interage** com o cliente do Black Desert Online de nenhuma forma ativa.

### O que ele faz

- **Ping Automatizado:** Varre as conexões de rede ativas estabelecidas pelo processo `BlackDesert64.exe` através da biblioteca `psutil`. Ele localiza a faixa de portas de comunicação da Pearl Abyss (faixas `8880-8890` e `9000-9010`), priorizando os canais principais de gameplay (`8889` ou `9009`). A latência é medida via `socket` puro (UDP/TCP) até o IP descoberto.
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

O executável é assinado com certificado self-signed, que garante a integridade do arquivo (não foi alterado após a publicação) e tem timestamp válido. Por ser um projeto gratuito e de código aberto, não usamos certificado comercial pago — o que significa que o Windows SmartScreen pode exibir um alerta na primeira execução. A confiança vem do código-fonte auditável, disponível neste repositório.

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
│   ├── config.py        # Variáveis de ambiente e algoritmo de varredura dinâmica de IPs
│   ├── fps.py           # pywintrace para "escutar" os eventos do Windows (ETW) do provedor Microsoft-Windows-DXGI (monitor de FPS)
│   ├── ping.py          # Lógica de comunicação de rede
│   ├── overlay.py       # Interface gráfica e loop assíncrono
│   └── main.py          # Ponto de entrada (Entrypoint) do programa
├── tests/
│    ├── diagnostico_conexoes_bdo.py # Script de teste das portas remotas do BDO
├── .gitignore           # Para que o repositório tenha apenas pastas e arquivos relevantes ao projeto
├── BDO_SA_Ping.iss      # Script de inno setup para criar o instalador do BDO_SA_Ping
├── BDO_SA_Ping.spec     # Especificações da criação do BDO_SA_Ping.exe
├── LICENSE              # Licença MIT do projeto
├── pyping.bat           # Inicializador rápido para Windows
├── README.md            # Documentação do projeto
├── requirements.txt     # Para instalação dos pacotes essenciais para execução do projeto
└── version_info.txt     # Para descrição de versão do projeto
```

---

## 🛠️ Como Configurar e Executar

### Pré-requisitos

- **Python 3.x** instalado no seu computador.
- Biblioteca **psutil** instalada (`pip install psutil`).

### Execução Rápida (Windows)

1. Baixe ou clone este repositório no seu computador.
2. Dê dois cliques no arquivo `pyping.bat` localizado na raiz do projeto.
3. O overlay aparecerá na sua tela instantaneamente.

### Fechar aplicativo

Caso queira fechar a aplicação, basta clicar com o **botão direito do mouse** em cima do BDO Ping.

### Execução via Terminal

Caso prefira rodar manualmente pelo terminal ou prompt de comando na raiz do projeto:

```bash
python -m src.main
```

---

## ⚙️ Personalização

As configurações de intervalos de varredura e taxas de atualização podem ser personalizadas diretamente no arquivo `src/config.py`:

```python
NOME_PROCESSO_EXE = "BlackDesert64.exe"  # Nome do executável do jogo
INTERVALO_FPS_MS = 500                   # Tempo de atualização do número de FPS na tela
INTERVALO_MILISSEGUNDOS = 1000          # Tempo de atualização da checagem do Ping e conexões
```

*Nota: O script gerencia de forma inteligente a descoberta do IP e da porta remota, eliminando a necessidade de definir manualmente os endereços de servidores da distribuidora.*

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
