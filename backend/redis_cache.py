
import redis
import json

# Conectando ao Redis
conexao = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


# Salvando a partida completa no Redis
def salvar_partida(partida):

    chave = f"partida:{partida['id']}"

    dados = json.dumps(partida)

    # A partida fica salva por 300 segundos (5 minutos)
    conexao.setex(chave, 300, dados)

    print("Partida salva no Redis!")


# Buscando uma partida no Redis
def buscar_partida(id_partida):

    chave = f"partida:{id_partida}"

    dados = conexao.get(chave)

    if dados is None:
        print("CACHE MISS: partida não encontrada!")
        return None

    print("CACHE HIT: partida encontrada!")

    return json.loads(dados)


# Consultando o tempo restante
def consultar_ttl(id_partida):

    chave = f"partida:{id_partida}"

    tempo = conexao.ttl(chave)

    print(f"Tempo restante: {tempo} segundos")

    return tempo


# Excluindo uma partida
def excluir_partida(id_partida):

    chave = f"partida:{id_partida}"

    conexao.delete(chave)

    print("Partida excluída!")
