from pydantic import BaseModel


class Jogada(BaseModel):
    cor: str


class NovoJogador(BaseModel):
    jogador: str