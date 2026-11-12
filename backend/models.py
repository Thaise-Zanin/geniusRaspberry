from pydantic import BaseModel

# Dados recebidos quando o jogador envia uma jogada
class Jogada(BaseModel):
    cor: str

# Dados recebidos ao iniciar uma nova partida
class NovoJogador(BaseModel):
    jogador: str