# Genius — Frontend

Frontend do jogo Genius desenvolvido com HTML, CSS e JavaScript.

## Como executar

Entre na pasta do frontend:

```bash
cd frontend
```

Inicie o servidor:

```bash
python3 -m http.server 5500
```

No navegador, acesse:

```text
http://localhost:5500
```

No Windows, utilize `python` no lugar de `python3`.

## Configuração

O frontend possui dois modos de funcionamento:

- **Modo simulado:** permite testar a interface sem os componentes físicos.
- **Modo real:** conecta o frontend ao backend executado na Raspberry Pi.

As configurações ficam em `js/api.js`:

```javascript
const CONFIG = {
  USAR_MOCK: false,
  BASE_URL: 'http://localhost:8000',
  WS_URL: 'ws://localhost:8000/ws'
};
```

Para utilizar a Raspberry Pi, configure `BASE_URL` e `WS_URL` com o endereço IP da Raspberry Pi.

## Comunicação com o backend

O frontend utiliza os seguintes recursos da API:

| Método | Rota | Descrição |
|---|---|---|
| GET | `/estatisticas?jogador=NOME` | Consulta as estatísticas do jogador |
| POST | `/partidas` | Inicia uma nova partida |
| WebSocket | `/ws` | Recebe os eventos da partida |

### Eventos recebidos pelo WebSocket

- `sequencia`: envia a sequência de cores que deve ser memorizada.
- `botao`: informa a cor pressionada e se a jogada está correta.
- `acerto`: informa que o jogador completou o nível.
- `fim`: informa o encerramento da partida, com nível e pontuação.

Exemplo de sequência:

```json
{
  "tipo": "sequencia",
  "nivel": 1,
  "pontuacao": 0,
  "sequencia": ["verde", "vermelho"]
}
```

## Funcionamento do jogo

1. O jogador informa seu nome.
2. O frontend apresenta a sequência de cores.
3. O jogador reproduz a sequência utilizando os botões físicos conectados à Raspberry Pi.
4. O backend valida as jogadas.
5. A cada sequência completada corretamente, o jogador avança de nível.
6. Se errar ou deixar o tempo acabar, a partida é encerrada.

O frontend apresenta as cores e as informações da partida. Os botões físicos e os LEDs são controlados pela Raspberry Pi.
