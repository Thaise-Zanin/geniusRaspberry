
from pydantic import BaseModel

# Modelo dos dados recebidos nas jogadas
class Jogada(BaseModel):
    cor: str
