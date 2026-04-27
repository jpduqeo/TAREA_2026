"""
Modulo de configuracion de la base de datos con SQLAlchemy.

Configura la conexion a SQLite, la sesion de base de datos y
provee las funciones para inicializar el esquema y los datos iniciales.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

URL_BASE_DATOS = os.getenv("DATABASE_URL", "sqlite:///./data/gamestore.db")

motor = create_engine(
    URL_BASE_DATOS,
    connect_args={"check_same_thread": False},
    echo=False,
)

FabricaSesion = sessionmaker(autocommit=False, autoflush=False, bind=motor)

BaseModelo = declarative_base()


def obtener_sesion() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI para inyectar sesiones de base de datos.

    Usa el patron de contexto con yield para garantizar que la sesion
    se cierre siempre al finalizar el request, incluso si hay errores.

    Yields:
        Session: Sesion activa de SQLAlchemy lista para usar.

    Example:
        >>> @app.get("/games")
        ... def listar(db: Session = Depends(obtener_sesion)):
        ...     return db.query(ModeloVideojuego).all()
    """
    sesion = FabricaSesion()
    try:
        yield sesion
    finally:
        sesion.close()


def inicializar_bd() -> None:
    """
    Crea las tablas de la base de datos y carga los datos iniciales.

    Importa los modelos ORM para que SQLAlchemy los registre antes
    de ejecutar el CREATE TABLE. Carga juegos de ejemplo si la BD
    esta vacia.

    Example:
        >>> inicializar_bd()  # Llamar al inicio de la aplicacion
    """
    from src.infrastructure.db import modelos  # noqa: F401

    BaseModelo.metadata.create_all(bind=motor)

    from src.infrastructure.db.datos_iniciales import cargar_juegos_ejemplo
    sesion = FabricaSesion()
    try:
        cargar_juegos_ejemplo(sesion)
    finally:
        sesion.close()
