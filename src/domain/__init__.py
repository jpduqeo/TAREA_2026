"""
Paquete de la capa de dominio de GameStore AI.

Contiene entidades, interfaces de repositorios y excepciones
del negocio. Completamente independiente de frameworks externos.
"""

from .entidades import Videojuego, MensajeChat, ContextoChat
from .repositorios import IRepositorioVideojuegos, IRepositorioChat
from .excepciones import (
    ExcepcionDominio,
    VideojuegoNoEncontrado,
    DatosVideojuegoInvalidos,
    StockInsuficiente,
    ErrorServicioChat,
)

__all__ = [
    "Videojuego",
    "MensajeChat",
    "ContextoChat",
    "IRepositorioVideojuegos",
    "IRepositorioChat",
    "ExcepcionDominio",
    "VideojuegoNoEncontrado",
    "DatosVideojuegoInvalidos",
    "StockInsuficiente",
    "ErrorServicioChat",
]
