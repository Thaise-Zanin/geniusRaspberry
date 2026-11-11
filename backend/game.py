import random
import uuid
import sqlite3

from pathlib import Path
from threading import Lock
from datetime import datetime, timezone


CORES = ["vermelho", "azul", "verde", "amarelo"]

partidas = {}
trava = Lock()

BANCO = Path(__file__).with_name("genius.db")


def conectar_banco():
    return sqlite3.connect(BANCO)


def criar_tabelas():
    with conectar_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador TEXT NOT NULL,
                pontuacao INTEGER NOT NULL,
                nivel INTEGER NOT NULL,
                resultado TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)


def calcular_tempo_led(nivel):
    tempo = 800 - (nivel - 1) * 50
    return max(250, tempo)


def registrar_resultado(partida, resultado):
    if partida.get("registrada"):
        return

    with conectar_banco() as conexao:
        conexao.execute("""
            INSERT INTO historico
            (jogador, pontuacao, nivel, resultado, data)
            VALUES (?, ?, ?, ?, ?)
        """, (
            partida["jogador"],
            partida["pontuacao"],
            partida["nivel"],
            resultado,
            datetime.now(timezone.utc).isoformat()
        ))

    partida["registrada"] = True


def iniciar_partida(jogador="Anônimo"):
    id_partida = str(uuid.uuid4())

    partida = {
        "id": id_partida,
        "jogador": jogador,
        "sequencia": [random.choice(CORES)],
        "nivel": 1,
        "pontuacao": 0,
        "indice_resposta": 0,
        "tempo_led_ms": calcular_tempo_led(1),
        "status": "aguardando_jogada",
        "registrada": False
    }

    with trava:
        partidas[id_partida] = partida

    return partida.copy()


def buscar_partida(id_partida):
    with trava:
        partida = partidas.get(id_partida)

        if partida is None:
            return None

        return partida.copy()


def validar_jogada(id_partida, cor):
    with trava:
        partida = partidas.get(id_partida)

        if partida is None:
            return None

        if partida["status"] == "derrota":
            return {"erro": "A partida já foi encerrada."}

        if cor not in CORES:
            return {"erro": "Cor inválida."}

        indice = partida["indice_resposta"]

        if cor != partida["sequencia"][indice]:
            partida["status"] = "derrota"
            registrar_resultado(partida, "derrota")
            return partida.copy()

        partida["indice_resposta"] += 1

        if partida["indice_resposta"] == len(partida["sequencia"]):
            partida["pontuacao"] += 10
            partida["nivel"] += 1
            partida["tempo_led_ms"] = calcular_tempo_led(
                partida["nivel"]
            )

            partida["sequencia"].append(random.choice(CORES))
            partida["indice_resposta"] = 0

            return {
                **partida.copy(),
                "resultado": "nivel_concluido"
            }

        return {
            **partida.copy(),
            "resultado": "correta"
        }


def encerrar_por_tempo(id_partida):
    with trava:
        partida = partidas.get(id_partida)

        if partida is None:
            return None

        if partida["status"] == "derrota":
            return partida.copy()

        partida["status"] = "derrota"
        registrar_resultado(partida, "derrota")

        return partida.copy()


def reiniciar_partida(id_partida):
    with trava:
        partida_antiga = partidas.get(id_partida)

        if partida_antiga is None:
            return None

        jogador = partida_antiga["jogador"]

        partida = {
            "id": id_partida,
            "jogador": jogador,
            "sequencia": [random.choice(CORES)],
            "nivel": 1,
            "pontuacao": 0,
            "indice_resposta": 0,
            "tempo_led_ms": calcular_tempo_led(1),
            "status": "aguardando_jogada",
            "registrada": False
        }

        partidas[id_partida] = partida

        return partida.copy()


def buscar_estatisticas(jogador):
    with conectar_banco() as conexao:
        cursor = conexao.execute("""
            SELECT
                COUNT(*),
                SUM(CASE WHEN resultado = 'vitoria' THEN 1 ELSE 0 END),
                SUM(CASE WHEN resultado = 'derrota' THEN 1 ELSE 0 END),
                COALESCE(MAX(pontuacao), 0),
                COALESCE(AVG(pontuacao), 0),
                COALESCE(MAX(nivel), 0)
            FROM historico
            WHERE jogador = ?
        """, (jogador,))

        dados = cursor.fetchone()

    return {
        "jogador": jogador,
        "partidas": dados[0],
        "vitorias": dados[1] or 0,
        "derrotas": dados[2] or 0,
        "melhor_pontuacao": dados[3],
        "media_pontuacao": round(dados[4], 2),
        "maior_nivel": dados[5]
    }


criar_tabelas()
