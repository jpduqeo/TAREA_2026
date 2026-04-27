"""
Implementacion del repositorio de videojuegos con SQLAlchemy.

Implementa IRepositorioVideojuegos usando SQLite como motor de base
de datos. Convierte entre modelos ORM y entidades del dominio.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entidades import Videojuego
from src.domain.repositorios import IRepositorioVideojuegos
from src.infrastructure.db.modelos import ModeloVideojuego


class RepositorioSQLVideojuegos(IRepositorioVideojuegos):
    """
    Repositorio concreto de videojuegos usando SQLAlchemy y SQLite.

    Implementa todos los metodos del contrato IRepositorioVideojuegos
    usando consultas SQLAlchemy. Convierte automaticamente entre
    modelos ORM y entidades del dominio en cada operacion.

    Attributes:
        sesion (Session): Sesion de SQLAlchemy inyectada por FastAPI.

    Example:
        >>> repo = RepositorioSQLVideojuegos(sesion=db)
        >>> juegos = repo.obtener_todos()
    """

    def __init__(self, sesion: Session) -> None:
        """
        Inicializa el repositorio con la sesion de base de datos.

        Args:
            sesion (Session): Sesion activa de SQLAlchemy inyectada
                              mediante Depends(obtener_sesion) en FastAPI.
        """
        self.sesion = sesion

    def obtener_todos(self) -> List[Videojuego]:
        """
        Recupera todos los videojuegos de la base de datos.

        Returns:
            List[Videojuego]: Lista de entidades del dominio.
        """
        modelos = self.sesion.query(ModeloVideojuego).all()
        return [self._modelo_a_entidad(m) for m in modelos]

    def obtener_por_id(self, juego_id: int) -> Optional[Videojuego]:
        """
        Busca un videojuego por su ID en la base de datos.

        Args:
            juego_id (int): ID a buscar.

        Returns:
            Optional[Videojuego]: La entidad si existe, None si no.
        """
        modelo = self.sesion.query(ModeloVideojuego).filter(
            ModeloVideojuego.id == juego_id
        ).first()
        return self._modelo_a_entidad(modelo) if modelo else None

    def obtener_por_genero(self, genero: str) -> List[Videojuego]:
        """
        Filtra videojuegos por genero (busqueda parcial, sin distincion de mayusculas).

        Args:
            genero (str): Genero a filtrar.

        Returns:
            List[Videojuego]: Juegos del genero indicado.
        """
        modelos = self.sesion.query(ModeloVideojuego).filter(
            ModeloVideojuego.genero.ilike(f"%{genero}%")
        ).all()
        return [self._modelo_a_entidad(m) for m in modelos]

    def obtener_por_plataforma(self, plataforma: str) -> List[Videojuego]:
        """
        Filtra videojuegos por plataforma (busqueda parcial, sin distincion de mayusculas).

        Args:
            plataforma (str): Plataforma a filtrar.

        Returns:
            List[Videojuego]: Juegos de la plataforma indicada.
        """
        modelos = self.sesion.query(ModeloVideojuego).filter(
            ModeloVideojuego.plataforma.ilike(f"%{plataforma}%")
        ).all()
        return [self._modelo_a_entidad(m) for m in modelos]

    def guardar(self, juego: Videojuego) -> Videojuego:
        """
        Persiste un videojuego nuevo o actualiza uno existente.

        Si el juego tiene ID, actualiza los campos del registro existente.
        Si no tiene ID, crea un nuevo registro y asigna el ID generado.

        Args:
            juego (Videojuego): Entidad a guardar.

        Returns:
            Videojuego: La entidad guardada con ID asignado.
        """
        if juego.id is not None:
            modelo = self.sesion.query(ModeloVideojuego).filter(
                ModeloVideojuego.id == juego.id
            ).first()
            if modelo:
                modelo.titulo = juego.titulo
                modelo.desarrollador = juego.desarrollador
                modelo.genero = juego.genero
                modelo.plataforma = juego.plataforma
                modelo.precio = juego.precio
                modelo.stock = juego.stock
                modelo.descripcion = juego.descripcion
        else:
            modelo = self._entidad_a_modelo(juego)
            self.sesion.add(modelo)

        self.sesion.commit()
        self.sesion.refresh(modelo)
        return self._modelo_a_entidad(modelo)

    def eliminar(self, juego_id: int) -> bool:
        """
        Elimina un videojuego de la base de datos.

        Args:
            juego_id (int): ID del juego a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existia.
        """
        modelo = self.sesion.query(ModeloVideojuego).filter(
            ModeloVideojuego.id == juego_id
        ).first()
        if not modelo:
            return False
        self.sesion.delete(modelo)
        self.sesion.commit()
        return True

    def _modelo_a_entidad(self, modelo: ModeloVideojuego) -> Videojuego:
        """
        Convierte un modelo ORM a una entidad del dominio.

        Args:
            modelo (ModeloVideojuego): Modelo ORM de SQLAlchemy.

        Returns:
            Videojuego: Entidad del dominio equivalente.
        """
        return Videojuego(
            id=modelo.id,
            titulo=modelo.titulo,
            desarrollador=modelo.desarrollador,
            genero=modelo.genero,
            plataforma=modelo.plataforma,
            precio=modelo.precio,
            stock=modelo.stock,
            descripcion=modelo.descripcion or "",
        )

    def _entidad_a_modelo(self, entidad: Videojuego) -> ModeloVideojuego:
        """
        Convierte una entidad del dominio a un modelo ORM.

        Args:
            entidad (Videojuego): Entidad del dominio.

        Returns:
            ModeloVideojuego: Modelo ORM equivalente.
        """
        return ModeloVideojuego(
            titulo=entidad.titulo,
            desarrollador=entidad.desarrollador,
            genero=entidad.genero,
            plataforma=entidad.plataforma,
            precio=entidad.precio,
            stock=entidad.stock,
            descripcion=entidad.descripcion,
        )
