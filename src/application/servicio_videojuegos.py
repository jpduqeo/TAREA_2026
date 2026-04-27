"""
Modulo del servicio de videojuegos de la capa de aplicacion.

Implementa los casos de uso del catalogo: listar, buscar, filtrar,
crear, actualizar, eliminar y vender videojuegos. Coordina entre
las entidades del dominio y el repositorio de persistencia.
"""

from typing import List

from src.domain.entidades import Videojuego
from src.domain.repositorios import IRepositorioVideojuegos
from src.domain.excepciones import VideojuegoNoEncontrado, DatosVideojuegoInvalidos
from src.application.dtos import (
    VideojuegoDTO,
    FiltroVideojuegoDTO,
    VentaDTO,
    ResultadoVentaDTO,
)


class ServicioVideojuegos:
    """
    Servicio de aplicacion para gestionar el catalogo de videojuegos.

    Orquesta los casos de uso coordinando entre las entidades del dominio
    y el repositorio de acceso a datos. Recibe el repositorio por
    inyeccion de dependencias para mantener el desacoplamiento.

    Attributes:
        repositorio (IRepositorioVideojuegos): Repositorio de videojuegos.

    Example:
        >>> repo = RepositorioSQLVideojuegos(db)
        >>> servicio = ServicioVideojuegos(repositorio=repo)
        >>> juegos = servicio.listar_catalogo()
    """

    def __init__(self, repositorio: IRepositorioVideojuegos) -> None:
        """
        Inicializa el servicio con el repositorio inyectado.

        Args:
            repositorio (IRepositorioVideojuegos): Implementacion del repositorio
                de videojuegos proveniente de la capa de infraestructura.
        """
        self.repositorio = repositorio

    def listar_catalogo(self) -> List[VideojuegoDTO]:
        """
        Retorna el catalogo completo de videojuegos disponibles.

        Returns:
            List[VideojuegoDTO]: Todos los juegos como DTOs.

        Example:
            >>> servicio.listar_catalogo()
            [VideojuegoDTO(titulo='Elden Ring', ...), ...]
        """
        juegos = self.repositorio.obtener_todos()
        return [self._entidad_a_dto(j) for j in juegos]

    def buscar_por_id(self, juego_id: int) -> VideojuegoDTO:
        """
        Busca un videojuego especifico por su ID.

        Args:
            juego_id (int): ID del videojuego a buscar.

        Returns:
            VideojuegoDTO: El videojuego encontrado.

        Raises:
            VideojuegoNoEncontrado: Si no existe juego con ese ID.

        Example:
            >>> servicio.buscar_por_id(1)
            VideojuegoDTO(titulo='Elden Ring', ...)
        """
        juego = self.repositorio.obtener_por_id(juego_id)
        if juego is None:
            raise VideojuegoNoEncontrado(juego_id)
        return self._entidad_a_dto(juego)

    def buscar_con_filtros(self, filtro: FiltroVideojuegoDTO) -> List[VideojuegoDTO]:
        """
        Filtra videojuegos por genero y/o plataforma.

        Si no se especifica ningun filtro, retorna el catalogo completo.

        Args:
            filtro (FiltroVideojuegoDTO): Criterios de busqueda opcionales.

        Returns:
            List[VideojuegoDTO]: Juegos que cumplen los filtros.

        Example:
            >>> filtro = FiltroVideojuegoDTO(genero="RPG")
            >>> servicio.buscar_con_filtros(filtro)
        """
        if filtro.genero:
            juegos = self.repositorio.obtener_por_genero(filtro.genero)
        elif filtro.plataforma:
            juegos = self.repositorio.obtener_por_plataforma(filtro.plataforma)
        else:
            juegos = self.repositorio.obtener_todos()
        return [self._entidad_a_dto(j) for j in juegos]

    def listar_disponibles(self) -> List[VideojuegoDTO]:
        """
        Retorna solo los videojuegos con stock mayor a cero.

        Util para mostrar al usuario unicamente los juegos que puede comprar.

        Returns:
            List[VideojuegoDTO]: Juegos con al menos una unidad en inventario.

        Example:
            >>> servicio.listar_disponibles()
        """
        todos = self.repositorio.obtener_todos()
        disponibles = [j for j in todos if j.tiene_stock()]
        return [self._entidad_a_dto(j) for j in disponibles]

    def registrar_juego(self, dto: VideojuegoDTO) -> VideojuegoDTO:
        """
        Agrega un nuevo videojuego al catalogo.

        Args:
            dto (VideojuegoDTO): Datos del nuevo videojuego.

        Returns:
            VideojuegoDTO: El juego registrado con su ID asignado.

        Raises:
            DatosVideojuegoInvalidos: Si los datos no cumplen las reglas de negocio.
        """
        try:
            entidad = self._dto_a_entidad(dto)
        except ValueError as e:
            raise DatosVideojuegoInvalidos(str(e))
        guardado = self.repositorio.guardar(entidad)
        return self._entidad_a_dto(guardado)

    def actualizar_juego(self, juego_id: int, dto: VideojuegoDTO) -> VideojuegoDTO:
        """
        Actualiza los datos de un videojuego existente en el catalogo.

        Args:
            juego_id (int): ID del juego a actualizar.
            dto (VideojuegoDTO): Nuevos datos del videojuego.

        Returns:
            VideojuegoDTO: El juego actualizado.

        Raises:
            VideojuegoNoEncontrado: Si el juego no existe.
            DatosVideojuegoInvalidos: Si los nuevos datos son invalidos.
        """
        existente = self.repositorio.obtener_por_id(juego_id)
        if existente is None:
            raise VideojuegoNoEncontrado(juego_id)
        try:
            entidad = self._dto_a_entidad(dto)
            entidad.id = juego_id
        except ValueError as e:
            raise DatosVideojuegoInvalidos(str(e))
        actualizado = self.repositorio.guardar(entidad)
        return self._entidad_a_dto(actualizado)

    def eliminar_juego(self, juego_id: int) -> bool:
        """
        Elimina un videojuego del catalogo.

        Args:
            juego_id (int): ID del juego a eliminar.

        Returns:
            bool: True si fue eliminado correctamente.

        Raises:
            VideojuegoNoEncontrado: Si el juego no existe.
        """
        if self.repositorio.obtener_por_id(juego_id) is None:
            raise VideojuegoNoEncontrado(juego_id)
        return self.repositorio.eliminar(juego_id)

    def procesar_venta(self, juego_id: int, cantidad: int) -> ResultadoVentaDTO:
        """
        Procesa la compra de un videojuego reduciendo su stock automaticamente.

        Implementa la regla de negocio: al vender, el stock se reduce de
        inmediato. Usa el metodo vender() de la entidad Videojuego que
        aplica todas las validaciones de negocio necesarias.

        Flujo:
        1. Verifica que el juego exista.
        2. Llama a juego.vender(cantidad) para aplicar la regla de negocio.
        3. Persiste el juego con el stock actualizado.
        4. Retorna el resultado de la transaccion.

        Args:
            juego_id (int): ID del videojuego a vender.
            cantidad (int): Unidades a vender. Debe ser >= 1.

        Returns:
            ResultadoVentaDTO: Confirmacion con el stock restante.

        Raises:
            VideojuegoNoEncontrado: Si el juego no existe en el catalogo.
            DatosVideojuegoInvalidos: Si el stock es insuficiente.

        Example:
            >>> servicio.procesar_venta(juego_id=1, cantidad=1)
            ResultadoVentaDTO(titulo='Elden Ring', cantidad_vendida=1, ...)
        """
        juego = self.repositorio.obtener_por_id(juego_id)
        if juego is None:
            raise VideojuegoNoEncontrado(juego_id)
        try:
            juego.vender(cantidad)
        except ValueError as e:
            raise DatosVideojuegoInvalidos(str(e))
        self.repositorio.guardar(juego)
        return ResultadoVentaDTO(
            juego_id=juego.id,
            titulo=juego.titulo,
            cantidad_vendida=cantidad,
            stock_restante=juego.stock,
            mensaje=(
                f"Compra exitosa. Se vendieron {cantidad} "
                f"unidad(es) de '{juego.titulo}'. "
                f"Stock restante: {juego.stock}."
            ),
        )

    def _entidad_a_dto(self, juego: Videojuego) -> VideojuegoDTO:
        """
        Convierte una entidad Videojuego a un VideojuegoDTO.

        Args:
            juego (Videojuego): Entidad del dominio.

        Returns:
            VideojuegoDTO: DTO equivalente.
        """
        return VideojuegoDTO(
            id=juego.id,
            titulo=juego.titulo,
            desarrollador=juego.desarrollador,
            genero=juego.genero,
            plataforma=juego.plataforma,
            precio=juego.precio,
            stock=juego.stock,
            descripcion=juego.descripcion,
        )

    def _dto_a_entidad(self, dto: VideojuegoDTO) -> Videojuego:
        """
        Convierte un VideojuegoDTO a una entidad del dominio.

        Args:
            dto (VideojuegoDTO): DTO a convertir.

        Returns:
            Videojuego: Entidad del dominio creada desde el DTO.

        Raises:
            ValueError: Si los datos no pasan las validaciones de la entidad.
        """
        return Videojuego(
            id=dto.id,
            titulo=dto.titulo,
            desarrollador=dto.desarrollador,
            genero=dto.genero,
            plataforma=dto.plataforma,
            precio=dto.precio,
            stock=dto.stock,
            descripcion=dto.descripcion,
        )
