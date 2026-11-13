# Genius Raspberry

Esse trabalho é baseado no jogo **Genius** de memória e raciocínio onde um objeto demosntra uma cor e o jadagor a aperta em sequência. Nesta versão: o jogador memória uma sequência de cores exibidas na tela do computador e a repete apertando **botões físicos** ligados a uma **Raspberry Pi**, os LEDs acem ao preciosar os botões e um **buzzer** é tocado em acertos e erros. A cada nível completado a sequência cresce uma cor para memorizar.

O projeto é dividido em três partes que conversam entre si:

 Parte | Tecnologia | Responsabilidade |
| ----- | ---------- | ---------------- |
| **Hardware** (`main.py`) | Python, `gpiozero`, `requests` | Lê os botões, acende LEDs, toca o buzzer e envia as jogadas para a API |
| **Backend** (`backend/`) | Python, FastAPI, SQLite, Redis | Gera as sequências, valida jogadas, controla tempo e pontuação, guarda o histórico e avisa o frontend em tempo real |
| **Frontend** (`frontend/`) | HTML, CSS e JavaScript | Mostra o tabuleiro, a sequência, o placar e as estatísticas do jogador |

## Como funciona

1. O jogador digita seu nome no frontend e inicia o jogo. Após uma conexão WebSocket (`/ws`) é aberta com o backend enviando `POST /partidas`.
2. O backend cria a partida e envia a sequência ao frontend pelo WebSocket (evento `sequencia`).
3. O frontend pisca a sequência de cores na tela.
4. O jogador reproduz a sequência nos botões físicos. A Raspberry Pi acende o LED da cor apertada e envia a jogada para `POST /hardware/botao`.
5. O backend valida a jogada e responde à Raspberry Pi, que toca o buzzer (bipe curto ao completar o nível, longo ao perder). Ao mesmo tempo, transmite o resultado ao frontend pelo WebSocket (`botao` e, depois, `acerto` ou `fim`).
6. Ao completar a sequência, o jogador sobe de nível e uma nova cor é adicionada assim o backend envia uma nova `sequencia`. Ao errar, a partida termina e o resultado é salvo no banco.

### Regras do Jogo

- A partida sempre será iniciada com 1 a cor, ao avançar de nível 1 cor é adicioanda.
- Cada nível completado vale **10** pontos.
- Errar uma cor encerra a partida (jogador perdeu).
- Cores apresentadas: `vermelho`, `azul`, `verde` e `amarelo`.
- Cada partida tem o resultado armazenado na tabela `histórico` (utilizando SQLite).
- Apenas uma partida é ativada por vez, o hardware envia as jogadas para essa partida.

---

## Estrutura do repositório

```text
geniusRaspberry/
├── main.py                 # Hardware: botões, LEDs e buzzer (Raspberry Pi)
├── backend/
│   ├── main.py             # API FastAPI, WebSocket e temporizadores
│   ├── game.py             # Lógica do jogo, SQLite e estatísticas
│   ├── models.py           # Modelos Pydantic (Jogada, NovoJogador)
│   ├── redis_cache.py      # Cache das partidas no Redis
│   ├── teste_redis.py      # Script manual para testar o Redis
│   ├── requirements.txt    # Dependências do backend
│   └── genius.db           # Banco SQLite com o histórico de partidas
└── frontend/
    ├── index.html          # Página inicial (nome do jogador e estatísticas)
    ├── pages/jogo.html     # Tela do jogo
    ├── js/
    │   ├── api.js          # Configuração, cliente da API e modo simulado (Mock)
    │   ├── main.js         # Cabeçalho, utilitários e página inicial
    │   ├── jogo.js         # Fluxo da partida e tratamento dos eventos
    │   └── animations.js   # Animação das cores
    └── *.css               # Estilos (global, dashboard e jogo)
```

## Hardware (Raspberry Pi)

O arquivo `main.py`, da raiz roda na Raspberry Pi. Ele escuta os quatro botões, acende o LED da cor apertada e envia cada jogada para o backend em uma thread separada, usando uma fila. Assim a leitura dos botões nunca fica travada esperando a rede.

### Endereço da API

O hardware envia as jogadas para `http://localhost:8000/hardware/botao`. Se o backend estiver em outro dispositivo, altere a constante `API_URL` no início do `main.py`.

---

## Backend (FastAPI)

### Requisitos

- Python 3.10 ou superior (o código usa a sintaxe `NovoJogador | None`)
- **Redis** instalado e rodando em `localhost:6379`
- Dependências em `backend/requirements.txt`: `fastapi`, `uvicorn[standard]`, `redis`

### Persistência

- **SQLite** (`backend/genius.db`): histórico definitivo de partidas, criado automaticamente na primeira execução.
- **Redis**: cache das partidas em andamento, com expiração de 300 segundos. A leitura tenta o Redis primeiro e usa a memória como alternativa.

### Rotas HTTP

Documentação interativa (Swagger) em `http://localhost:8000/docs`.

| Método | Rota | Descrição |
| ------ | ---- | --------- |
| GET | `/` | Mensagem de boas-vindas e link da documentação |
| GET | `/health` | Verifica se o servidor está online |
| POST | `/partidas` (ou `/partida/iniciar`) | Inicia uma partida. Corpo: `{"jogador": "Nome"}` |
| GET | `/partida/{id_partida}` | Consulta o estado da partida |
| GET | `/partida/{id_partida}/sequencia` | Retorna a sequência, o nível e o tempo do LED |
| POST | `/partida/{id_partida}/jogar` | Envia uma jogada pela API. Corpo: `{"cor": "verde"}` |
| POST | `/hardware/botao` | Recebe a jogada dos botões físicos para a partida ativa. Corpo: `{"cor": "verde"}` |
| POST | `/partida/{id_partida}/reiniciar` | Reinicia a partida |
| GET | `/estatisticas?jogador=NOME` | Estatísticas do jogador |

Exemplo de resposta de `/estatisticas`:

```json
{
  "jogador": "Ana",
  "partidas": 5,
  "vitorias": 0,
  "derrotas": 5,
  "melhor_pontuacao": 80,
  "media_pontuacao": 42.0,
  "maior_nivel": 9
}
```

### WebSocket `/ws`

O backend transmite eventos para todos os clientes conectados:

| Evento (`tipo`) | Quando acontece | Campos |
| --------------- | --------------- | ------ |
| `sequencia` | Início da partida e a cada novo nível | `nivel`, `pontuacao`, `sequencia` |
| `botao` | A cada jogada recebida | `cor`, `correto` |
| `acerto` | Nível completado | `nivel`, `pontuacao` |
| `fim` | Erro ou tempo esgotado | `nivel`, `pontuacao` |

---

## Frontend

- **Início (`index.html`)**: nome do jogador, demonstração animada e três indicadores (maior nível, melhor pontuação e partidas realizadas).
- **Jogo (`pages/jogo.html`)**: placar, tabuleiro com as quatro cores, mensagens de status, barra de progresso da sequência e tela de fim de jogo.

O nome do jogador é salvo no `localStorage` do navegador.

## Como executar

### 1. Clonar o repositório

#### Todos os passos abaixo devem ser realizados dentro da Raspberry.

```bash
git clone https://github.com/Thaise-Zanin/geniusRaspberry.git
cd geniusRaspberry
```

### 2. Instalar e iniciar o Redis (Raspberry Pi / Debian)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
redis-cli ping        # deve responder PONG
```
### 3. Backend

Execute sempre a partir da **raiz** do projeto.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Teste em `http://localhost:8000/health` ou abra `http://localhost:8000/docs`.

### 4. Hardware (na Raspberry Pi)

Com o backend rodando, abra outro terminal na raiz do projeto:

```bash
source venv/bin/activate
pip install gpiozero requests
python3 main.py
```

Irá retornar `Hardware Genius conectado!`. Use `Ctrl+C` para encerrar: os LEDs, os botões e o buzzer são liberados automaticamente.

### 5. Frontend

```bash
cd frontend
python3 -m http.server 5500
```

Acesse `http://localhost:5500` no seu navegador. No Windows, use `python` no lugar de `python3`.

### 6. Jogar

1. Abra o frontend, digite seu nome e clique em **INICIAR JOGO**.
2. Memorize a sequência que piscar na tela.
3. Quando aparecer "Sua vez!", repita a sequência nos botões físicos.

---

## Cenários de uso

**Tudo na Raspberry Pi.** Rode Redis, backend, hardware e frontend na própria Pi e abra `http://localhost:5500` nela. Nenhuma alteração de configuração é necessária.

**Backend na Pi, frontend no navegador.** Em `frontend/js/api.js`, troque `localhost` pelo IP da Raspberry Pi:

```javascript
BASE_URL: 'http://192.168.0.50:8000',
WS_URL: 'ws://192.168.0.50:8000/ws',
```

O backend já aceita conexões externas (`--host 0.0.0.0`) e libera CORS para qualquer origem.

**Para apenas testar a interface:** Defina `USAR_MOCK: true` em `api.js` e abra o frontend. Não é preciso Redis, backend nem Raspberry Pi.

**Para testar somente a API:** Use a documentação em `/docs` para iniciar uma partida e enviar jogadas em `POST /partida/{id}/jogar`, sem o hardware.

**Testar somente o Redis.**

```bash
cd backend
python3 teste_redis.py
```

---

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
| ------- | -------------- | ----------- |
| `redis.exceptions.ConnectionError` ao iniciar a partida | Redis não está rodando | `sudo systemctl start redis-server` |
| `ImportError: attempted relative import` | Backend iniciado de dentro da pasta `backend/` | Rode `uvicorn backend.main:app` a partir da raiz |
| Hardware responde "Não existe partida ativa" | Nenhuma partida foi iniciada | Clique em **INICIAR JOGO** no frontend antes de apertar os botões |
| Erro de conexão no terminal do hardware | Backend inacessível em `API_URL` | Verifique se o backend está de pé e a URL no `main.py` |

---

## Tecnologias

- Python 3, FastAPI e Uvicorn
- SQLite e Redis
- gpiozero e requests (Raspberry Pi)
- HTML5, CSS3 e JavaScript (ES6+), com Fetch API e WebSocket