
import redis
import json

# Conectando ao Redis
conexao = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


# Salvar uma partida no Redis
def salvar_partida(id_partida, sequencia, nivel, pontuacao):

    chave = f"partida:{id_partida}"

    dados = {
        "sequencia": sequencia,
        "nivel": nivel,
        "pontuacao": pontuacao
    }

    # Salva os dados com validade de 300 segundos (5 minutos)
    conexao.setex(chave, 300, json.dumps(dados))

    print("Partida salva no Redis!")


# Buscar uma partida no Redis
def buscar_partida(id_partida):

    chave = f"partida:{id_partida}"

    dados = conexao.get(chave)

    if dados is None:
        print("CACHE MISS: partida não encontrada!")
        return None

    print("CACHE HIT: partida encontrada!")

    return json.loads(dados)


# Consultar o tempo restante da partida
def consultar_ttl(id_partida):

    chave = f"partida:{id_partida}"

    tempo = conexao.ttl(chave)

    print(f"Tempo restante: {tempo} segundos")

    return tempo


# Excluir uma partida
def excluir_partida(id_partida):

    chave = f"partida:{id_partida}"

    conexao.delete(chave)

    print("Partida excluída!")
