"""
Modulo de excepciones del dominio de la tienda de videojuegos.

Define errores especificos del negocio para un manejo de excepciones
mas preciso y descriptivo que las excepciones genericas de Python.
"""


class ExcepcionDominio(Exception):
    """
    Clase base para todas las excepciones del dominio.

    Permite capturar cualquier error de negocio con un solo except.

    Args:
        mensaje (str): Descripcion del error ocurrido.
    """

    def __init__(self, mensaje: str) -> None:
        self.mensaje = mensaje
        super().__init__(self.mensaje)


class VideojuegoNoEncontrado(ExcepcionDominio):
    """
    Se lanza cuando no existe un videojuego con el ID solicitado.

    Args:
        juego_id (int): ID del videojuego que no fue encontrado.

    Example:
        >>> raise VideojuegoNoEncontrado(42)
        VideojuegoNoEncontrado: Videojuego con ID 42 no encontrado en el catalogo.
    """

    def __init__(self, juego_id: int) -> None:
        super().__init__(
            f"Videojuego con ID {juego_id} no encontrado en el catalogo."
        )
        self.juego_id = juego_id


class DatosVideojuegoInvalidos(ExcepcionDominio):
    """
    Se lanza cuando los datos de un videojuego no cumplen las reglas de negocio.

    Args:
        mensaje (str): Descripcion del error de validacion.

    Example:
        >>> raise DatosVideojuegoInvalidos("El precio debe ser mayor a 0")
    """

    def __init__(self, mensaje: str) -> None:
        super().__init__(f"Datos de videojuego invalidos: {mensaje}")


class StockInsuficiente(ExcepcionDominio):
    """
    Se lanza al intentar vender mas unidades de las disponibles en inventario.

    Args:
        titulo (str): Titulo del juego con stock insuficiente.
        disponible (int): Unidades actualmente en stock.
        solicitado (int): Unidades que se intentaron vender.

    Example:
        >>> raise StockInsuficiente("God of War", 1, 5)
    """

    def __init__(self, titulo: str, disponible: int, solicitado: int) -> None:
        super().__init__(
            f"Stock insuficiente para '{titulo}'. "
            f"Disponible: {disponible}, solicitado: {solicitado}."
        )
        self.disponible = disponible
        self.solicitado = solicitado


class ErrorServicioChat(ExcepcionDominio):
    """
    Se lanza cuando ocurre un fallo en el servicio de chat con IA.

    Args:
        mensaje (str): Descripcion del fallo ocurrido.

    Example:
        >>> raise ErrorServicioChat("Error al conectar con Gemini AI")
    """

    def __init__(self, mensaje: str) -> None:
        super().__init__(f"Error en el servicio de chat: {mensaje}")
