"""
Modulo de interfaces de repositorios del dominio.

Define los contratos abstractos que deben implementar los repositorios
en la capa de infraestructura. Permite que el dominio sea completamente
independiente de la tecnologia de persistencia utilizada.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entidades import Videojuego, MensajeChat


class IRepositorioVideojuegos(ABC):
    """
    Contrato para el acceso y gestion de videojuegos en el almacenamiento.

    Las implementaciones concretas se ubican en la capa de infraestructura.
    Permite cambiar la base de datos sin afectar la logica de negocio.

    Example:
        >>> class RepositorioSQLVideojuegos(IRepositorioVideojuegos):
        ...     def obtener_todos(self) -> List[Videojuego]:
        ...         return self.db.query(ModeloVideojuego).all()
    """

    @abstractmethod
    def obtener_todos(self) -> List[Videojuego]:
        """
        Obtiene todos los videojuegos del catalogo.

        Returns:
            List[Videojuego]: Lista completa. Lista vacia si no hay juegos.
        """
        pass

    @abstractmethod
    def obtener_por_id(self, juego_id: int) -> Optional[Videojuego]:
        """
        Busca un videojuego por su identificador unico.

        Args:
            juego_id (int): ID del videojuego a buscar.

        Returns:
            Optional[Videojuego]: El juego si existe, None si no.
        """
        pass

    @abstractmethod
    def obtener_por_genero(self, genero: str) -> List[Videojuego]:
        """
        Filtra videojuegos por genero.

        Args:
            genero (str): Genero a filtrar, ej: "RPG", "Accion".

        Returns:
            List[Videojuego]: Juegos del genero indicado.
        """
        pass

    @abstractmethod
    def obtener_por_plataforma(self, plataforma: str) -> List[Videojuego]:
        """
        Filtra videojuegos por plataforma.

        Args:
            plataforma (str): Plataforma a filtrar, ej: "PS5", "PC".

        Returns:
            List[Videojuego]: Juegos disponibles en esa plataforma.
        """
        pass

    @abstractmethod
    def guardar(self, juego: Videojuego) -> Videojuego:
        """
        Persiste un videojuego nuevo o actualiza uno existente.

        Args:
            juego (Videojuego): Juego a guardar o actualizar.

        Returns:
            Videojuego: El juego guardado con ID asignado si era nuevo.
        """
        pass

    @abstractmethod
    def eliminar(self, juego_id: int) -> bool:
        """
        Elimina un videojuego del catalogo.

        Args:
            juego_id (int): ID del juego a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existia.
        """
        pass


class IRepositorioChat(ABC):
    """
    Contrato para gestionar el historial de conversaciones del chat.

    Define como guardar y recuperar mensajes para mantener la memoria
    conversacional del asistente de IA entre interacciones.
    """

    @abstractmethod
    def guardar_mensaje(self, mensaje: MensajeChat) -> MensajeChat:
        """
        Persiste un mensaje de chat en el historial.

        Args:
            mensaje (MensajeChat): Mensaje a guardar.

        Returns:
            MensajeChat: El mensaje guardado con su ID asignado.
        """
        pass

    @abstractmethod
    def obtener_historial_sesion(
        self, sesion_id: str, limite: Optional[int] = None
    ) -> List[MensajeChat]:
        """
        Recupera el historial de mensajes de una sesion.

        Args:
            sesion_id (str): Identificador de la sesion.
            limite (Optional[int]): Maximo de mensajes. None para todos.

        Returns:
            List[MensajeChat]: Mensajes en orden cronologico.
        """
        pass

    @abstractmethod
    def eliminar_historial_sesion(self, sesion_id: str) -> int:
        """
        Borra todos los mensajes de una sesion.

        Args:
            sesion_id (str): Sesion a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        pass

    @abstractmethod
    def obtener_mensajes_recientes(
        self, sesion_id: str, cantidad: int
    ) -> List[MensajeChat]:
        """
        Recupera los ultimos N mensajes de una sesion.

        Args:
            sesion_id (str): Identificador de la sesion.
            cantidad (int): Numero de mensajes a recuperar.

        Returns:
            List[MensajeChat]: Ultimos mensajes en orden cronologico.
        """
        pass
