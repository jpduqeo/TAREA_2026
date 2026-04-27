"""
Modulo de modelos ORM de la base de datos.

Define las clases que mapean las tablas SQLite usando SQLAlchemy.
Son la representacion tecnica de las entidades del dominio
en la capa de persistencia.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index
from src.infrastructure.db.base_datos import BaseModelo


class ModeloVideojuego(BaseModelo):
    """
    Modelo ORM que representa la tabla 'videojuegos' en la base de datos.

    Attributes:
        id (int): Clave primaria autoincremental.
        titulo (str): Nombre del videojuego. Maximo 200 caracteres.
        desarrollador (str): Empresa creadora. Maximo 150 caracteres.
        genero (str): Genero del juego. Maximo 80 caracteres.
        plataforma (str): Plataforma compatible. Maximo 80 caracteres.
        precio (float): Precio en dolares.
        stock (int): Unidades disponibles en inventario.
        descripcion (str): Descripcion detallada (texto libre).

    Example:
        >>> modelo = ModeloVideojuego(
        ...     titulo="Elden Ring",
        ...     desarrollador="FromSoftware",
        ...     genero="RPG",
        ...     plataforma="PC",
        ...     precio=59.99,
        ...     stock=15
        ... )
    """

    __tablename__ = "videojuegos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    desarrollador = Column(String(150), nullable=False)
    genero = Column(String(80), nullable=False)
    plataforma = Column(String(80), nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    descripcion = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_videojuegos_genero", "genero"),
        Index("ix_videojuegos_plataforma", "plataforma"),
    )

    def __repr__(self) -> str:
        """Representacion legible del modelo para debugging."""
        return (
            f"<ModeloVideojuego(id={self.id}, titulo='{self.titulo}', "
            f"plataforma='{self.plataforma}', precio={self.precio})>"
        )


class ModeloHistorialChat(BaseModelo):
    """
    Modelo ORM que representa la tabla 'historial_chat'.

    Almacena cada mensaje de las conversaciones para mantener
    la memoria conversacional del asistente de IA.

    Attributes:
        id (int): Clave primaria autoincremental.
        sesion_id (str): Identificador de la sesion de conversacion.
        rol (str): Emisor del mensaje: 'usuario' o 'asistente'.
        contenido (str): Texto del mensaje.
        fecha_hora (datetime): Momento de envio en UTC.

    Example:
        >>> msg = ModeloHistorialChat(
        ...     sesion_id="jugador_001",
        ...     rol="usuario",
        ...     contenido="Busco RPGs para PS5",
        ...     fecha_hora=datetime.utcnow()
        ... )
    """

    __tablename__ = "historial_chat"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sesion_id = Column(String(100), nullable=False)
    rol = Column(String(20), nullable=False)
    contenido = Column(Text, nullable=False)
    fecha_hora = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_historial_chat_sesion_id", "sesion_id"),
    )

    def __repr__(self) -> str:
        """Representacion legible del modelo para debugging."""
        return (
            f"<ModeloHistorialChat(id={self.id}, sesion='{self.sesion_id}', "
            f"rol='{self.rol}')>"
        )
