
import random
import uuid
from threading import Lock

# Cores disponíveis no jogo
CORES = ["vermelho", "azul", "verde", "amarelo"]

# Armazena as partidas enquanto o servidor está em execução
partidas = {}
trava = Lock()

# Calcula o tempo de exibição dos LEDs conforme o nível
def calcular_tempo_led(nivel):
    tempo = 800 - (nivel - 1) * 50
    return max(250, tempo)

# Cria uma nova partida com sequência e pontuação inicial
def iniciar_partida():
    id_partida = str(uuid.uuid4())

    partida = {
        "id": id_partida,
        "sequencia": [random.choice(CORES)],
        "nivel": 1,
        "pontuacao": 0,
        "indice_resposta": 0,
        "tempo_led_ms": calcular_tempo_led(1),
        "status": "aguardando_jogada"
    }

    with trava:
        partidas[id_partida] = partida

    return partida.copy()

# Busca uma partida pelo seu identificador
def buscar_partida(id_partida):
    with trava:
        partida = partidas.get(id_partida)

        if partida is None:
            return None

        return partida.copy()

# Verifica se a cor escolhida pelo jogador está correta
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
            return partida.copy()

        partida["indice_resposta"] += 1

        if partida["indice_resposta"] == len(partida["sequencia"]):
            partida["pontuacao"] += 10
            partida["nivel"] += 1
            partida["tempo_led_ms"] = calcular_tempo_led(partida["nivel"])
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

# Reinicia uma partida, voltando ao nível inicial
def reiniciar_partida(id_partida):
    with trava:
        if id_partida not in partidas:
            return None

        partida = {
            "id": id_partida,
            "sequencia": [random.choice(CORES)],
            "nivel": 1,
            "pontuacao": 0,
            "indice_resposta": 0,
            "tempo_led_ms": calcular_tempo_led(1),
            "status": "aguardando_jogada"
        }

        partidas[id_partida] = partida

        return partida.copy()
