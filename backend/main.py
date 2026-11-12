import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .game import (
    iniciar_partida,
    buscar_partida,
    validar_jogada,
    encerrar_por_tempo,
    reiniciar_partida,
    buscar_estatisticas
)

from .models import Jogada, NovoJogador

# Configura as informações principais da API
app = FastAPI(
    title="Genius API",
    description="API para gerenciamento do jogo Genius",
    version="1.0.0"
)

# Permite a comunicação entre a API e o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Define os tempos utilizados durante as rodadas
TEMPO_RESPOSTA = 60
TEMPO_PREPARACAO = 1
TEMPO_COR_MS = 600
INTERVALO_MS = 250

# Armazena as conexões WebSocket e a partida ativa
conexoes = []
partida_ativa = None
temporizadores = {}

# Adiciona uma nova conexão WebSocket
async def conectar_websocket(websocket: WebSocket):
    await websocket.accept()
    conexoes.append(websocket)

# Remove uma conexão WebSocket
def desconectar_websocket(websocket: WebSocket):
    if websocket in conexoes:
        conexoes.remove(websocket)

# Envia uma atualização para todos os clientes conectados
async def transmitir(evento):
    desconectados = []

    for conexao in conexoes:
        try:
            await conexao.send_json(evento)
        except Exception:
            desconectados.append(conexao)

    for conexao in desconectados:
        desconectar_websocket(conexao)

# Mantém a conexão WebSocket aberta para receber mensagens
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await conectar_websocket(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        desconectar_websocket(websocket)

# Cancela o temporizador de uma partida
def cancelar_temporizador(id_partida):
    tarefa = temporizadores.pop(id_partida, None)

    if tarefa and not tarefa.done():
        tarefa.cancel()

# Inicia a contagem do tempo para o jogador responder
def iniciar_temporizador(id_partida, tempo=TEMPO_RESPOSTA):
    cancelar_temporizador(id_partida)

    temporizadores[id_partida] = asyncio.create_task(
        verificar_tempo(id_partida, tempo)
    )

# Verifica se o jogador respondeu dentro do tempo permitido
async def verificar_tempo(id_partida, tempo):
    tarefa_atual = asyncio.current_task()

    try:
        await asyncio.sleep(tempo)

        partida = buscar_partida(id_partida)

        if partida is None or partida["status"] == "derrota":
            return

        resultado = encerrar_por_tempo(id_partida)

        if resultado is None:
            return
        
        # Avisa os clientes que o tempo acabou
        await transmitir({
            "tipo": "fim",
            "nivel": resultado["nivel"],
            "pontuacao": resultado["pontuacao"]
        })

    except asyncio.CancelledError:
        pass

    finally:
        if temporizadores.get(id_partida) is tarefa_atual:
            temporizadores.pop(id_partida, None)

# Envia a sequência de cores para os clientes conectados
async def enviar_sequencia(partida):
    await transmitir({
        "tipo": "sequencia",
        "nivel": partida["nivel"],
        "pontuacao": partida["pontuacao"],
        "sequencia": partida["sequencia"]
    })

    # Calcula o tempo necessário para exibir toda a sequência
    tempo_exibicao = (
        TEMPO_PREPARACAO
        + len(partida["sequencia"])
        * (TEMPO_COR_MS + INTERVALO_MS) / 1000
    )

    # Inicia o tempo de resposta depois da exibição
    iniciar_temporizador(
        partida["id"],
        tempo_exibicao + TEMPO_RESPOSTA
    )

# Rota inicial e verificação do servidor
@app.get("/")
def inicio():
    return {
        "mensagem": "Servidor Genius funcionando!",
        "documentacao": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "online"}


# Cria uma nova partida e envia a primeira sequência
@app.post("/partida/iniciar")
@app.post("/partidas")
async def criar_partida(dados: NovoJogador | None = None):
    global partida_ativa

    nome = dados.jogador.strip() if dados else "Anônimo"

    if not nome:
        nome = "Jogador"

    # Cancela o temporizador da partida anterior, se existir
    if partida_ativa:
        cancelar_temporizador(partida_ativa)

    partida = iniciar_partida(nome)
    partida_ativa = partida["id"]

    await enviar_sequencia(partida)

    return partida

# Consulta os dados de uma partida pelo identificador
@app.get("/partida/{id_partida}")
def consultar_partida(id_partida: str):
    partida = buscar_partida(id_partida)

    if partida is None:
        raise HTTPException(
            status_code=404,
            detail="Partida não encontrada."
        )

    return partida

# Consulta a sequência atual e o tempo dos LEDs
@app.get("/partida/{id_partida}/sequencia")
def consultar_sequencia(id_partida: str):
    partida = buscar_partida(id_partida)

    if partida is None:
        raise HTTPException(
            status_code=404,
            detail="Partida não encontrada."
        )

    return {
        "sequencia": partida["sequencia"],
        "nivel": partida["nivel"],
        "tempo_led_ms": partida["tempo_led_ms"]
    }

# Processa e valida uma jogada enviada pelo jogador ou hardware
async def processar_jogada(id_partida, cor):
    partida_anterior = buscar_partida(id_partida)

    if partida_anterior is None:
        raise HTTPException(
            status_code=404,
            detail="Partida não encontrada."
        )

    if partida_anterior["status"] == "derrota":
        raise HTTPException(
            status_code=400,
            detail="A partida já foi encerrada."
        )

    resultado = validar_jogada(id_partida, cor)

    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Partida não encontrada."
        )

    if "erro" in resultado:
        raise HTTPException(
            status_code=400,
            detail=resultado["erro"]
        )

    # Informa qual botão foi pressionado e se a resposta estava correta
    await transmitir({
        "tipo": "botao",
        "cor": cor,
        "correto": resultado["status"] != "derrota"
    })

    # Encerra o temporizador e avisa quando o jogador perde
    if resultado["status"] == "derrota":
        cancelar_temporizador(id_partida)

        await transmitir({
            "tipo": "fim",
            "nivel": resultado["nivel"],
            "pontuacao": resultado["pontuacao"]
        })

    # Envia uma nova sequência quando o jogador conclui o nível
    elif resultado.get("resultado") == "nivel_concluido":
        cancelar_temporizador(id_partida)

        await transmitir({
            "tipo": "acerto",
            "nivel": resultado["nivel"],
            "pontuacao": resultado["pontuacao"]
        })

        # Aguarda um pouco antes de iniciar a próxima rodada
        async def proxima_rodada():
            await asyncio.sleep(1.5)

            partida_atual = buscar_partida(id_partida)

            if partida_atual and partida_atual["status"] != "derrota":
                await enviar_sequencia(partida_atual)

        asyncio.create_task(proxima_rodada())

    else:
        # Reinicia a contagem após uma resposta correta
        iniciar_temporizador(id_partida)

    return resultado

# Recebe uma jogada enviada pela API
@app.post("/partida/{id_partida}/jogar")
async def jogar(id_partida: str, jogada: Jogada):
    return await processar_jogada(id_partida, jogada.cor)

# Recebe as cores enviadas pelos botões físicos da Raspberry Pi
@app.post("/hardware/botao")
async def receber_botao(jogada: Jogada):
    if not partida_ativa:
        raise HTTPException(
            status_code=400,
            detail="Não existe partida ativa."
        )

    return await processar_jogada(
        partida_ativa,
        jogada.cor.lower()
    )

# Reinicia uma partida e envia uma nova sequência
@app.post("/partida/{id_partida}/reiniciar")
async def reiniciar(id_partida: str):
    partida = reiniciar_partida(id_partida)

    if partida is None:
        raise HTTPException(
            status_code=404,
            detail="Partida não encontrada."
        )

    cancelar_temporizador(id_partida)

    await enviar_sequencia(partida)

    return partida

# Consulta as estatísticas de um jogador
@app.get("/estatisticas")
def estatisticas(jogador: str):
    nome = jogador.strip()

    if not nome:
        raise HTTPException(
            status_code=400,
            detail="Informe o nome do jogador."
        )

    return buscar_estatisticas(nome)
