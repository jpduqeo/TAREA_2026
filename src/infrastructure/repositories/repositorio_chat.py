"""
Implementacion del repositorio de chat con SQLAlchemy.

Implementa IRepositorioChat para persistir el historial de
conversaciones en la tabla 'historial_chat' de SQLite.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entidades import MensajeChat
from src.domain.repositorios import IRepositorioChat
from src.infrastructure.db.modelos import ModeloHistorialChat


class RepositorioSQLChat(IRepositorioChat):
    """
    Repositorio concreto del historial de chat usando SQLAlchemy.

    Persiste y recupera mensajes de la tabla 'historial_chat' en SQLite.
    Convierte entre modelos ORM y entidades del dominio en cada operacion.

    Attributes:
        sesion (Session): Sesion de SQLAlchemy inyectada por FastAPI.

    Example:
        >>> repo = RepositorioSQLChat(sesion=db)
        >>> repo.guardar_mensaje(mensaje)
        >>> historial = repo.obtener_historial_sesion("jugador_001")
    """

    def __init__(self, sesion: Session) -> None:
        """
        Inicializa el repositorio con la sesion de base de datos.

        Args:
            sesion (Session): Sesion activa de SQLAlchemy.
        """
        self.sesion = sesion

    def guardar_mensaje(self, mensaje: MensajeChat) -> MensajeChat:
        """
        Persiste un mensaje en el historial de chat.

        Args:
            mensaje (MensajeChat): Mensaje a guardar.

        Returns:
            MensajeChat: El mensaje con su ID asignado por la base de datos.
        """
        modelo = self._entidad_a_modelo(mensaje)
        self.sesion.add(modelo)
        self.sesion.commit()
        self.sesion.refresh(modelo)
        return self._modelo_a_entidad(modelo)

    def obtener_historial_sesion(
        self, sesion_id: str, limite: Optional[int] = None
    ) -> List[MensajeChat]:
        """
        Recupera el historial de mensajes de una sesion en orden cronologico.

        Args:
            sesion_id (str): Identificador de la sesion.
            limite (Optional[int]): Maximo de mensajes. None para todos.

        Returns:
            List[MensajeChat]: Mensajes de mas antiguo a mas reciente.
        """
        if limite is not None:
            modelos = (
                self.sesion.query(ModeloHistorialChat)
                .filter(ModeloHistorialChat.sesion_id == sesion_id)
                .order_by(ModeloHistorialChat.fecha_hora.desc())
                .limit(limite)
                .all()
            )
            modelos.reverse()
        else:
            modelos = (
                self.sesion.query(ModeloHistorialChat)
                .filter(ModeloHistorialChat.sesion_id == sesion_id)
                .order_by(ModeloHistorialChat.fecha_hora.asc())
                .all()
            )
        return [self._modelo_a_entidad(m) for m in modelos]

    def eliminar_historial_sesion(self, sesion_id: str) -> int:
        """
        Elimina todos los mensajes de una sesion de chat.

        Args:
            sesion_id (str): Sesion a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        cantidad = (
            self.sesion.query(ModeloHistorialChat)
            .filter(ModeloHistorialChat.sesion_id == sesion_id)
            .delete()
        )
        self.sesion.commit()
        return cantidad

    def obtener_mensajes_recientes(
        self, sesion_id: str, cantidad: int
    ) -> List[MensajeChat]:
        """
        Recupera los ultimos N mensajes de una sesion en orden cronologico.

        Args:
            sesion_id (str): Identificador de la sesion.
            cantidad (int): Numero de mensajes a recuperar.

        Returns:
            List[MensajeChat]: Ultimos mensajes de mas antiguo a mas reciente.
        """
        modelos = (
            self.sesion.query(ModeloHistorialChat)
            .filter(ModeloHistorialChat.sesion_id == sesion_id)
            .order_by(ModeloHistorialChat.fecha_hora.desc())
            .limit(cantidad)
            .all()
        )
        modelos.reverse()
        return [self._modelo_a_entidad(m) for m in modelos]

    def _modelo_a_entidad(self, modelo: ModeloHistorialChat) -> MensajeChat:
        """
        Convierte un modelo ORM a una entidad del dominio.

        Args:
            modelo (ModeloHistorialChat): Modelo ORM a convertir.

        Returns:
            MensajeChat: Entidad del dominio equivalente.
        """
        return MensajeChat(
            id=modelo.id,
            sesion_id=modelo.sesion_id,
            rol=modelo.rol,
            contenido=modelo.contenido,
            fecha_hora=modelo.fecha_hora or datetime.utcnow(),
        )

    def _entidad_a_modelo(self, entidad: MensajeChat) -> ModeloHistorialChat:
        """
        Convierte una entidad del dominio a un modelo ORM.

        Args:
            entidad (MensajeChat): Entidad del dominio a convertir.

        Returns:
            ModeloHistorialChat: Modelo ORM equivalente.
        """
        return ModeloHistorialChat(
            sesion_id=entidad.sesion_id,
            rol=entidad.rol,
            contenido=entidad.contenido,
            fecha_hora=entidad.fecha_hora,
        )
