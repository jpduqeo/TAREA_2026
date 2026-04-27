"""
Paquete de la capa de aplicacion de GameStore AI.

Contiene los servicios de casos de uso y los DTOs para transferencia
de datos. Depende del dominio pero no de la infraestructura.
"""

from .servicio_videojuegos import ServicioVideojuegos
from .servicio_chat import ServicioChat
from .dtos import (
    VideojuegoDTO,
    FiltroVideojuegoDTO,
    VentaDTO,
    ResultadoVentaDTO,
    SolicitudChatDTO,
    RespuestaChatDTO,
    HistorialMensajeDTO,
)

__all__ = [
    "ServicioVideojuegos",
    "ServicioChat",
    "VideojuegoDTO",
    "FiltroVideojuegoDTO",
    "VentaDTO",
    "ResultadoVentaDTO",
    "SolicitudChatDTO",
    "RespuestaChatDTO",
    "HistorialMensajeDTO",
]
