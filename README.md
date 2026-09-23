# BDO SA Ping Overlay 🎮📈

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/28e5a2c4-07fc-49ff-9df6-91f49547d2a6" />


Um utilitário leve e limpo desenvolvido em Python para monitorar a latência (ping) e FPS em tempo real diretamente na tela do jogo **Black Desert Online (Servidor SA)**. O programa cria uma sobreposição (overlay) transparente e móvel, permitindo que você acompanhe a estabilidade da sua conexão sem perder o foco na gameplay.

---
## 🛠️ Por que este projeto foi criado?
Como jogador de BDO, senti muita falta de um monitor de ping e FPS nativo dentro do jogo. Após sugerir essa implementação para a Pearl Abyss diversas vezes e não obter retorno, decidi criar uma solução própria, leve e focada na comunidade do servidor SA.

## ⚔️ Benefícios no Jogo:
- **Evite mortes em spots:** Monitore sua conexão em tempo real enquanto faz o seu grind e evite surpresas com picos de lag que podem destruir seus cristais.
- **Navegação segura:** Não perca o seu barco de vista por causa de dessincronização com o servidor, evitando ter que nadar longas distâncias para alcançá-lo.
- **Leve e Seguro:** Desenvolvido para não impactar o FPS do seu jogo e assinado digitalmente para garantir a segurança da instalação.

## ✨ Funcionalidades

* **Overlay Transparente:** Interface minimalista que remove as bordas do Windows e se integra ao jogo.
* **Sempre no Topo (Always on Top):** Garante que o contador de ping fique visível acima da janela do jogo.
* **Indicador Visual por Cor:**
* Ping
  * 🟢 **Verde:** Conexão excelente (< 40ms)
  * 🟡 **Amarelo:** Conexão moderada (< 90ms)
  * 🔴 **Vermelho:** Latência alta ou Falha de conexão
* FPS
  * 🟢 **Verde:** FPS Bom (> 60 FPS)
  * 🟡 **Amarelo:** FPS Razoável (entre 59 FPS e 20 FPS)
  * 🔴 **Vermelho:** FPS Ruim (< 20 FPS)
  * ⚪ **Cinza:** FPS -- (> 1000 FPS ou falha)

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
    ├── fps.py           # pywintrace para "escutar" os eventos do Windows (ETW) do provedor Microsoft-Windows-DXGI monitor de FPS
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

### Fechar aplicativo
Caso queira fechar aplicação basta clicar com direito do mouse em cima do BDO ping
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
