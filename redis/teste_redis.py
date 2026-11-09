
from redis_cache import (
    salvar_partida,
    buscar_partida,
    consultar_ttl,
    excluir_partida
)

# Criando uma partida fictícia
salvar_partida(
    id_partida=123,
    sequencia=["vermelho", "azul", "verde"],
    nivel=3,
    pontuacao=20
)

print("\n--- PRIMEIRA CONSULTA ---")

partida = buscar_partida(123)
print(partida)

print("\n--- SEGUNDA CONSULTA ---")

buscar_partida(123)

print("\n--- CONSULTANDO TTL ---")

consultar_ttl(123)

print("\n--- CONSULTANDO PARTIDA INEXISTENTE ---")

buscar_partida(999)

print("\n--- EXCLUINDO PARTIDA ---")

excluir_partida(123)

print("\n--- CONSULTANDO NOVAMENTE ---")

buscar_partida(123)
