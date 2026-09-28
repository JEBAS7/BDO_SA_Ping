# BDO SA Ping Overlay 🎮📈

<img width="1920" height="1080" alt="Overlay de ping e FPS sobre o Black Desert Online" src="https://github.com/user-attachments/assets/1d9a682d-b0f6-4bcb-a177-4567bcc51e0c" />

Um utilitário leve e limpo desenvolvido em Python para monitorar a latência (ping) e o FPS em tempo real diretamente na tela do jogo **Black Desert Online (Servidor SA)**. O programa cria uma sobreposição (overlay) transparente e móvel, permitindo que você acompanhe a estabilidade da sua conexão sem perder o foco na gameplay.

---

## 🛠️ Por que este projeto foi criado?

Como jogador de BDO, senti muita falta de um monitor de ping e FPS nativo dentro do jogo. Após sugerir essa implementação para a Pearl Abyss diversas vezes e não obter retorno, decidi criar uma solução própria, leve e focada na comunidade do servidor SA.

## ⚔️ Benefícios no Jogo

- **Evite mortes em spots:** Monitore sua conexão em tempo real enquanto faz o seu grind e evite surpresas com picos de lag que podem destruir seus cristais.
- **Navegação segura:** Não perca o seu barco de vista por causa de dessincronização com o servidor, evitando ter que nadar longas distâncias para alcançá-lo.
- **Leve e seguro:** Desenvolvido para não impactar o FPS do seu jogo. Não injeta código, não lê a memória do jogo e não interage com o processo do BDO — apenas usa APIs nativas do Windows (ETW/DXGI) para o FPS e sockets UDP/TCP para medir a latência, da mesma forma que ferramentas como Discord e Steam.

## ✨ Funcionalidades

- **Detecção dinâmica de servidor:** Identifica automaticamente o IP e a porta de gameplay ativa do BDO, adaptando-se instantaneamente quando você troca de canal (ex.: Balenos, Serendia, Temporada) sem quebrar o monitoramento e sem precisar reiniciar o programa.
- **Overlay transparente:** Interface minimalista que remove as bordas do Windows e se integra ao jogo.
- **Sempre no topo (Always on Top):** Garante que o contador de ping e FPS fique visível acima da janela do jogo.
- **Indicador visual por cor:**

  **Ping**
  - 🟢 **Verde:** Conexão excelente (< 40 ms)
  - 🟡 **Amarelo:** Conexão moderada (40 ms a 89 ms)
  - 🔴 **Vermelho:** Latência alta (≥ 90 ms) ou falha de conexão

  **FPS**
  - 🟢 **Verde:** FPS bom (≥ 60 FPS)
  - 🟡 **Amarelo:** FPS razoável (entre 20 e 59 FPS)
  - 🔴 **Vermelho:** FPS ruim (< 20 FPS)
  - 🟢 **Verde, "999" fixo:** a captura está se autocorrigindo internamente (reinício rápido de sessão durante loadings/transições) — não é uma leitura real, apenas evita mostrar "--" piscando nesse meio-tempo
  - ⚪ **Cinza, "--":** falha real de captura (jogo fechado ou captura sem conseguir se recuperar)

- **Arrastável:** Clique e arraste o contador para qualquer lugar da tela com o mouse.
- **Multithread e seguro:** Desenvolvido com multi-threading para garantir que os testes de rede não travem a sua tela.

---

## ⚠️ Limitações conhecidas

O overlay não aparece em modo **Tela Cheia** (exclusiva), pois esse modo faz o jogo assumir o controle direto da GPU, ignorando o compositor do Windows (DWM) — nenhuma janela externa consegue desenhar por cima nesse caso. A captura de ping/FPS continua rodando normalmente por trás.

Use **Tela Cheia em Janela** (borderless) para que o overlay apareça normalmente.

## 🛡️ Não é um cheat — como funciona

Este projeto é um **monitor externo**, não um cheat. Ele **não interage** com o cliente do Black Desert Online de nenhuma forma ativa.

### O que ele faz

- **Ping automatizado:** Varre as conexões de rede ativas estabelecidas pelo processo `BlackDesert64.exe` através da biblioteca `psutil`. Ele localiza as faixas de portas de comunicação da Pearl Abyss (`8880-8890` e `9000-9010`), priorizando os canais principais de gameplay (`8889` ou `9009`). A latência é medida via `socket` puro (UDP/TCP) até o IP descoberto.
- **FPS:** Obtém contadores via **ETW (Event Tracing for Windows)** no provedor público `Microsoft-Windows-DXGI`. É o próprio Windows reportando quantos frames foram apresentados por segundo, via `pywintrace`. Nenhum hook em DirectX, nenhuma injeção.
- **Detecção de jogo ativo:** Usa `win32gui` + `psutil` apenas para verificar se o processo `BlackDesert64` está em primeiro plano — nada é lido ou escrito nele.
- **Interface:** Overlay Tkinter transparente, sempre no topo. Uma janela comum do Windows, como Discord ou Steam.

### O que ele NÃO faz

- ❌ Não usa `ReadProcessMemory` / `WriteProcessMemory`
- ❌ Não usa `CreateRemoteThread` / injeção de DLL
- ❌ Não usa `SetWindowsHookEx` (nem de teclado, nem de mouse)
- ❌ Não faz hook em DirectX / DXGI / OpenGL
- ❌ Não abre handle com acesso à memória do processo do jogo (a `psutil` consulta apenas informações básicas, como nome e conexões de rede, com permissão limitada de consulta)
- ❌ Não registra hotkeys globais — a interação é só com clique direito (fechar) e arraste (mover) na própria janela

> **Aviso:** este é um projeto independente da comunidade, sem qualquer vínculo com a Pearl Abyss. Use por sua conta e risco.

### Assinatura

O executável é assinado com certificado self-signed, que garante a integridade do arquivo (não foi alterado após a publicação) e tem timestamp válido. Por ser um projeto gratuito e de código aberto, não usamos certificado comercial pago — o que significa que o Windows SmartScreen pode exibir um alerta na primeira execução. A confiança vem do código-fonte auditável, disponível neste repositório.

---

## 📁 Estrutura do Projeto

O repositório segue as boas práticas de arquitetura modular em Python:

```text
BDO_SA_Ping/
├── assets/
│   ├── BDO.ico          # Ícone do aplicativo
│   └── img.png          # Print da tela do Black Desert Online com o BDO Ping
├── src/
│   ├── __init__.py      # Inicializador do pacote
│   ├── config.py        # Variáveis de configuração e algoritmo de varredura dinâmica de IPs
│   ├── fps.py           # pywintrace para "escutar" os eventos ETW do provedor Microsoft-Windows-DXGI (monitor de FPS)
│   ├── ping.py          # Lógica de comunicação de rede
│   ├── overlay.py       # Interface gráfica e loop assíncrono
│   └── main.py          # Ponto de entrada (entrypoint) do programa
├── tests/
│   ├── __init__.py
│   └── diagnostico_conexoes_bdo.py  # Script de diagnóstico das portas remotas do BDO, usado para desenvolver a varredura dinâmica de IPs do config.py
├── .gitignore           # Mantém no repositório apenas pastas e arquivos relevantes ao projeto
├── BDO_SA_Ping.iss      # Script do Inno Setup para criar o instalador do BDO_SA_Ping
├── BDO_SA_Ping.spec     # Especificações do PyInstaller para gerar o BDO_SA_Ping.exe
├── LICENSE              # Licença Apache-2.0 license do projeto
├── pyping.bat           # Inicializador rápido para Windows
├── README.md            # Documentação do projeto
├── requirements.txt     # Pacotes necessários para a execução do projeto
└── version_info.txt     # Informações de versão do executável
```

---

## 🚀 Como Configurar e Executar

### Pré-requisitos

- **Python 3.x** instalado no seu computador.
- Dependências do projeto instaladas:

```bash
pip install -r requirements.txt
```

### Execução rápida (Windows)

1. Baixe ou clone este repositório no seu computador.
2. Dê dois cliques no arquivo `pyping.bat`, localizado na raiz do projeto.
3. O overlay aparecerá na sua tela instantaneamente.

### Fechar o aplicativo

Para fechar a aplicação, basta clicar com o **botão direito do mouse** em cima do BDO Ping.

### Execução via terminal

Caso prefira rodar manualmente pelo terminal ou prompt de comando, na raiz do projeto:

```bash
python -m src.main
```

---

## ⚙️ Personalização

As configurações de intervalos de varredura e taxas de atualização podem ser personalizadas diretamente no arquivo `src/config.py`:

```python
NOME_PROCESSO_EXE = "BlackDesert64.exe"  # Nome do executável do jogo
INTERVALO_FPS_MS = 500                   # Tempo de atualização do número de FPS na tela
INTERVALO_MILISSEGUNDOS = 1000           # Tempo de atualização da checagem do ping e das conexões
```

*Nota: O script gerencia de forma inteligente a descoberta do IP e da porta remota, eliminando a necessidade de definir manualmente os endereços de servidores da distribuidora.*

---

## 📄 Licença

Este projeto está sob a licença Apache 2.0. Veja o arquivo LICENSE para mais detalhes.

