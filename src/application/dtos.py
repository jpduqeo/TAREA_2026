"""
Modulo de DTOs (Data Transfer Objects) de la capa de aplicacion.

Los DTOs transfieren datos entre capas con validacion automatica
usando Pydantic. Garantizan que los datos entrantes sean correctos
antes de procesarlos en los servicios.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict


class VideojuegoDTO(BaseModel):
    """
    DTO para transferir informacion de videojuegos entre capas.

    Attributes:
        id (Optional[int]): ID del juego. None si es nuevo.
        titulo (str): Nombre del videojuego.
        desarrollador (str): Empresa desarrolladora.
        genero (str): Genero del juego (RPG, Accion, Deportes...).
        plataforma (str): Plataforma compatible (PS5, Xbox, PC, Switch).
        precio (float): Precio en dolares. Debe ser > 0.
        stock (int): Unidades en inventario. Debe ser >= 0.
        descripcion (str): Descripcion detallada del juego.

    Example:
        >>> dto = VideojuegoDTO(
        ...     titulo="Elden Ring",
        ...     desarrollador="FromSoftware",
        ...     genero="RPG",
        ...     plataforma="PC",
        ...     precio=59.99,
        ...     stock=15,
        ...     descripcion="RPG de mundo abierto"
        ... )
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    titulo: str
    desarrollador: str
    genero: str
    plataforma: str
    precio: float
    stock: int
    descripcion: str

    @field_validator("precio")
    @classmethod
    def validar_precio_positivo(cls, valor: float) -> float:
        """
        Verifica que el precio del videojuego sea mayor a cero.

        Args:
            valor (float): Precio a validar.

        Returns:
            float: El precio si es valido.

        Raises:
            ValueError: Si el precio es <= 0.
        """
        if valor <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return valor

    @field_validator("stock")
    @classmethod
    def validar_stock_no_negativo(cls, valor: int) -> int:
        """
        Verifica que el stock no sea un numero negativo.

        Args:
            valor (int): Stock a validar.

        Returns:
            int: El stock si es valido.

        Raises:
            ValueError: Si el stock es < 0.
        """
        if valor < 0:
            raise ValueError("El stock no puede ser negativo.")
        return valor


class FiltroVideojuegoDTO(BaseModel):
    """
    DTO para filtrar videojuegos por criterios opcionales.

    Attributes:
        genero (Optional[str]): Filtrar por genero. None para no filtrar.
        plataforma (Optional[str]): Filtrar por plataforma. None para no filtrar.

    Example:
        >>> filtro = FiltroVideojuegoDTO(genero="RPG", plataforma="PS5")
    """

    genero: Optional[str] = None
    plataforma: Optional[str] = None


class VentaDTO(BaseModel):
    """
    DTO para registrar la compra de un videojuego.

    Attributes:
        cantidad (int): Unidades a comprar. Minimo 1.

    Example:
        >>> compra = VentaDTO(cantidad=1)
    """

    cantidad: int = 1

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad_positiva(cls, valor: int) -> int:
        """
        Verifica que la cantidad a comprar sea al menos 1.

        Args:
            valor (int): Cantidad a validar.

        Returns:
            int: La cantidad si es valida.

        Raises:
            ValueError: Si la cantidad es menor a 1.
        """
        if valor < 1:
            raise ValueError("La cantidad a comprar debe ser al menos 1.")
        return valor


class ResultadoVentaDTO(BaseModel):
    """
    DTO con el resultado de una compra procesada exitosamente.

    Attributes:
        juego_id (int): ID del videojuego vendido.
        titulo (str): Nombre del videojuego vendido.
        cantidad_vendida (int): Unidades compradas en esta transaccion.
        stock_restante (int): Inventario disponible despues de la venta.
        mensaje (str): Confirmacion de la transaccion.

    Example:
        >>> resultado = ResultadoVentaDTO(
        ...     juego_id=1,
        ...     titulo="Elden Ring",
        ...     cantidad_vendida=1,
        ...     stock_restante=14,
        ...     mensaje="Compra realizada exitosamente."
        ... )
    """

    juego_id: int
    titulo: str
    cantidad_vendida: int
    stock_restante: int
    mensaje: str


class SolicitudChatDTO(BaseModel):
    """
    DTO para recibir mensajes del cliente en el endpoint de chat.

    Attributes:
        sesion_id (str): Identificador unico de la sesion del usuario.
        mensaje (str): Texto enviado por el cliente al asistente.

    Example:
        >>> solicitud = SolicitudChatDTO(
        ...     sesion_id="jugador_001",
        ...     mensaje="Busco juegos de RPG para PS5"
        ... )
    """

    sesion_id: str
    mensaje: str

    @field_validator("mensaje")
    @classmethod
    def validar_mensaje_no_vacio(cls, valor: str) -> str:
        """
        Verifica que el mensaje no este vacio.

        Args:
            valor (str): Mensaje a validar.

        Returns:
            str: El mensaje limpio si es valido.

        Raises:
            ValueError: Si el mensaje esta vacio.
        """
        if not valor or not valor.strip():
            raise ValueError("El mensaje no puede estar vacio.")
        return valor.strip()

    @field_validator("sesion_id")
    @classmethod
    def validar_sesion_no_vacia(cls, valor: str) -> str:
        """
        Verifica que el sesion_id no este vacio.

        Args:
            valor (str): Session ID a validar.

        Returns:
            str: El sesion_id limpio si es valido.

        Raises:
            ValueError: Si el sesion_id esta vacio.
        """
        if not valor or not valor.strip():
            raise ValueError("El sesion_id no puede estar vacio.")
        return valor.strip()


class RespuestaChatDTO(BaseModel):
    """
    DTO con la respuesta del asistente de IA al cliente.

    Attributes:
        sesion_id (str): Identificador de la sesion.
        mensaje_usuario (str): Mensaje original del cliente.
        respuesta_asistente (str): Respuesta generada por la IA.
        fecha_hora (datetime): Momento de la interaccion.

    Example:
        >>> respuesta = RespuestaChatDTO(
        ...     sesion_id="jugador_001",
        ...     mensaje_usuario="Busco RPGs",
        ...     respuesta_asistente="Tenemos Elden Ring disponible...",
        ...     fecha_hora=datetime.utcnow()
        ... )
    """

    sesion_id: str
    mensaje_usuario: str
    respuesta_asistente: str
    fecha_hora: datetime


class HistorialMensajeDTO(BaseModel):
    """
    DTO para mostrar un mensaje individual del historial de chat.

    Attributes:
        id (int): ID unico del mensaje.
        rol (str): Quien envio el mensaje: 'usuario' o 'asistente'.
        contenido (str): Texto del mensaje.
        fecha_hora (datetime): Cuando fue enviado.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    rol: str
    contenido: str
    fecha_hora: datetime
