from fastapi import FastAPI, HTTPException

from .game import (
    iniciar_partida,
    buscar_partida,
    validar_jogada,
    reiniciar_partida,
    buscar_ranking,
    buscar_estatisticas
)

from .models import Jogada


app = FastAPI(
    title="Genius API",
    description="API para gerenciamento do jogo Genius",
    version="1.0.0"
)


# Rotas iniciais e verificação do servidor
@app.get("/")
def inicio():
    return {
        "mensagem": "Servidor Genius funcionando!",
        "documentacao": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "online"}


# Rotas de gerenciamento das partidas
@app.post("/partida/iniciar")
def criar_partida():
    return iniciar_partida()


@app.get("/partida/{id_partida}")
def consultar_partida(id_partida: str):
    partida = buscar_partida(id_partida)

    if partida is None:
        raise HTTPException(
            status_code=404,
            detail="Partida não encontrada."
        )

    return partida


# Rotas de jogadas e validação das respostas
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


@app.post("/partida/{id_partida}/jogar")
def jogar(id_partida: str, jogada: Jogada):
    resultado = validar_jogada(id_partida, jogada.cor)

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

    return resultado


@app.post("/partida/{id_partida}/reiniciar")
def reiniciar(id_partida: str):
    partida = reiniciar_partida(id_partida)

    if partida is None:
        raise HTTPException(
            status_code=404,
            detail="Partida não encontrada."
        )

    return partida


# Rota do ranking dos 10 melhores resultados
@app.get("/ranking")
def ranking():
    return buscar_ranking()


# Rota das estatísticas de um jogador
@app.get("/estatisticas")
def estatisticas(jogador: str):
    nome = jogador.strip()

    if not nome:
        raise HTTPException(
            status_code=400,
            detail="Informe o nome do jogador."
        )

    return buscar_estatisticas(nome)
