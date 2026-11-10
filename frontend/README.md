# Genius — frontend (HTML + CSS + JS puro)

## Rodar
    cd genius-frontend
    python3 -m http.server 5500
Abra http://localhost:5500 (no Windows, use `python` no lugar de `python3`).

Começa em modo simulado (`USAR_MOCK: true` em js/api.js): o "servidor" é falso, o ranking fica no localStorage e, na vez do jogador, você clica nas cores para fingir os botões físicos.

## Na Raspberry Pi
Em js/api.js: `USAR_MOCK: false`, `BASE_URL` e `WS_URL` com o IP da Raspberry.

## Pontos a conectar no backend (propostas, alinhar com a equipe)
- GET /estatisticas?jogador=NOME -> {maiorNivel, melhorPontuacao, recordeGeral, partidas}
- GET /ranking -> [{jogador, nivel, pontuacao, data}]
- POST /partidas {jogador} -> inicia a partida
- WebSocket /ws envia: {tipo:'sequencia', nivel, pontuacao, sequencia:['verde',...]} | {tipo:'botao', cor, correto} | {tipo:'acerto', nivel, pontuacao} | {tipo:'fim', nivel, pontuacao, novoRecorde}
- Cores: verde, vermelho, amarelo, azul.

## Organização
js/api.js (config + API real + simulada) · js/animations.js (acende cores em ordem) · js/main.js (cabeçalho, dashboard) · js/jogo.js (tela de jogo) · js/ranking.js · css/ (um por página + global).
=======