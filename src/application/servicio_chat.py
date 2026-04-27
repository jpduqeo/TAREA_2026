"""
Modulo del servicio de chat con IA de la capa de aplicacion.

Implementa el caso de uso principal: procesar mensajes de clientes
y generar respuestas contextuales usando Google Gemini AI, con
memoria conversacional persistente por sesion.
"""

from datetime import datetime
from typing import List, Optional

from src.domain.entidades import MensajeChat, ContextoChat
from src.domain.repositorios import IRepositorioVideojuegos, IRepositorioChat
from src.domain.excepciones import ErrorServicioChat
from src.application.dtos import (
    SolicitudChatDTO,
    RespuestaChatDTO,
    HistorialMensajeDTO,
)


class ServicioChat:
    """
    Servicio de aplicacion para el chat inteligente con Google Gemini AI.

    Coordina el catalogo de videojuegos, el historial de conversacion
    y el servicio de IA para generar respuestas contextualizadas.
    La memoria conversacional permite interacciones coherentes y fluidas.

    Attributes:
        repositorio_juegos (IRepositorioVideojuegos): Acceso al catalogo.
        repositorio_chat (IRepositorioChat): Acceso al historial de chat.
        servicio_ia: Servicio de IA (GeminiService) para generar respuestas.

    Example:
        >>> servicio = ServicioChat(
        ...     repositorio_juegos=RepositorioSQLVideojuegos(db),
        ...     repositorio_chat=RepositorioSQLChat(db),
        ...     servicio_ia=GeminiService()
        ... )
        >>> respuesta = await servicio.procesar_mensaje(solicitud)
    """

    def __init__(
        self,
        repositorio_juegos: IRepositorioVideojuegos,
        repositorio_chat: IRepositorioChat,
        servicio_ia,
    ) -> None:
        """
        Inicializa el servicio con sus dependencias inyectadas.

        Args:
            repositorio_juegos (IRepositorioVideojuegos): Repositorio del catalogo.
            repositorio_chat (IRepositorioChat): Repositorio del historial de chat.
            servicio_ia: Servicio de IA para generar respuestas (GeminiService).
        """
        self.repositorio_juegos = repositorio_juegos
        self.repositorio_chat = repositorio_chat
        self.servicio_ia = servicio_ia

    async def procesar_mensaje(
        self, solicitud: SolicitudChatDTO
    ) -> RespuestaChatDTO:
        """
        Procesa el mensaje del cliente y genera una respuesta con IA.

        Flujo completo:
        1. Recupera el catalogo de videojuegos disponibles.
        2. Obtiene los ultimos 6 mensajes de la sesion como contexto.
        3. Genera una respuesta con Gemini AI usando catalogo + contexto.
        4. Persiste el mensaje del cliente y la respuesta del asistente.
        5. Retorna la respuesta como DTO.

        Args:
            solicitud (SolicitudChatDTO): Mensaje del cliente con su sesion_id.

        Returns:
            RespuestaChatDTO: Respuesta del asistente con timestamp.

        Raises:
            ErrorServicioChat: Si ocurre un fallo al procesar o llamar a la IA.

        Example:
            >>> req = SolicitudChatDTO(sesion_id="j001", mensaje="Busco RPGs")
            >>> resp = await servicio.procesar_mensaje(req)
            >>> print(resp.respuesta_asistente)
        """
        try:
            catalogo = self.repositorio_juegos.obtener_todos()
            mensajes_recientes = self.repositorio_chat.obtener_mensajes_recientes(
                sesion_id=solicitud.sesion_id, cantidad=6
            )
            contexto = ContextoChat(mensajes=mensajes_recientes, max_mensajes=6)
            respuesta_ia = await self.servicio_ia.generar_respuesta(
                mensaje_usuario=solicitud.mensaje,
                catalogo=catalogo,
                contexto=contexto,
            )
            ahora = datetime.utcnow()
            msg_cliente = MensajeChat(
                id=None,
                sesion_id=solicitud.sesion_id,
                rol="usuario",
                contenido=solicitud.mensaje,
                fecha_hora=ahora,
            )
            self.repositorio_chat.guardar_mensaje(msg_cliente)
            msg_asistente = MensajeChat(
                id=None,
                sesion_id=solicitud.sesion_id,
                rol="asistente",
                contenido=respuesta_ia,
                fecha_hora=datetime.utcnow(),
            )
            self.repositorio_chat.guardar_mensaje(msg_asistente)
            return RespuestaChatDTO(
                sesion_id=solicitud.sesion_id,
                mensaje_usuario=solicitud.mensaje,
                respuesta_asistente=respuesta_ia,
                fecha_hora=ahora,
            )
        except Exception as e:
            raise ErrorServicioChat(str(e)) from e

    def obtener_historial(
        self, sesion_id: str, limite: Optional[int] = 10
    ) -> List[HistorialMensajeDTO]:
        """
        Recupera el historial de mensajes de una sesion de chat.

        Args:
            sesion_id (str): Identificador de la sesion.
            limite (Optional[int]): Maximo de mensajes. Por defecto 10.

        Returns:
            List[HistorialMensajeDTO]: Mensajes del historial como DTOs.

        Example:
            >>> servicio.obtener_historial("jugador_001", limite=20)
        """
        mensajes = self.repositorio_chat.obtener_historial_sesion(
            sesion_id=sesion_id, limite=limite
        )
        return [
            HistorialMensajeDTO(
                id=m.id,
                rol=m.rol,
                contenido=m.contenido,
                fecha_hora=m.fecha_hora,
            )
            for m in mensajes
        ]

    def limpiar_sesion(self, sesion_id: str) -> int:
        """
        Elimina todo el historial de una sesion para reiniciar la conversacion.

        Args:
            sesion_id (str): Sesion a limpiar.

        Returns:
            int: Numero de mensajes eliminados.

        Example:
            >>> eliminados = servicio.limpiar_sesion("jugador_001")
        """
        return self.repositorio_chat.eliminar_historial_sesion(sesion_id)
