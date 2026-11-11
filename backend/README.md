# Genius - Backend

Backend do jogo Genius, desenvolvido em Python com FastAPI. Responsável por gerenciar as partidas, validar as jogadas, controlar a pontuação e armazenar os resultados.

## Estrutura

- `main.py`: rotas da API.
- `game.py`: lógica do jogo e gerenciamento das partidas.
- `models.py`: modelos de dados.
- `genius.db`: banco de dados com o histórico das partidas.

## Como executar

Ative o ambiente virtual:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install fastapi "uvicorn[standard]"
```

Inicie o servidor:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Documentação

Com o servidor iniciado, acesse:

[http://localhost:8000/docs](http://localhost:8000/docs)

## Rotas principais

| Método | Rota | Função |
| ------ | ---- | ------ |
| POST | `/partida/iniciar` | Iniciar partida |
| GET | `/partida/{id_partida}` | Consultar partida |
| POST | `/partida/{id_partida}/jogar` | Enviar jogada |
| POST | `/partida/{id_partida}/reiniciar` | Reiniciar partida |
| GET | `/estatisticas` | Consultar estatísticas |
