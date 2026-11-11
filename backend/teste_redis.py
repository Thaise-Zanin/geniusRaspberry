
from redis_cache import (
    salvar_partida,
    buscar_partida,
    consultar_ttl,
    excluir_partida
)

partida_teste = {
    "id": "teste123",
    "jogador": "Aline",
    "sequencia": ["vermelho", "azul", "verde"],
    "nivel": 3,
    "pontuacao": 20,
    "indice_resposta": 0,
    "tempo_led_ms": 700,
    "status": "aguardando_jogada",
    "registrada": False
}

salvar_partida(partida_teste)

print("\n--- BUSCANDO PARTIDA ---")
partida = buscar_partida("teste123")
print(partida)

print("\n--- CONSULTANDO TTL ---")
consultar_ttl("teste123")

print("\n--- EXCLUINDO PARTIDA ---")
excluir_partida("teste123")

print("\n--- BUSCANDO NOVAMENTE ---")
buscar_partida("teste123")
