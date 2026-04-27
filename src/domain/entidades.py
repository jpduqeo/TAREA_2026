"""
Modulo de entidades del dominio para la tienda de videojuegos.

Contiene las entidades principales del negocio: Videojuego, MensajeChat
y ContextoChat. Estas clases encapsulan la logica de negocio pura,
sin depender de ningun framework externo.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Videojuego:
    """
    Entidad que representa un videojuego en el catalogo de la tienda.

    Encapsula la logica de negocio relacionada con videojuegos,
    incluyendo validaciones de precio, stock y disponibilidad para venta.

    Attributes:
        id (Optional[int]): Identificador unico. None si es nuevo.
        titulo (str): Nombre del videojuego, ej: "God of War".
        desarrollador (str): Empresa que lo creo, ej: "Santa Monica Studio".
        genero (str): Genero del juego, ej: "Accion", "RPG", "Deportes".
        plataforma (str): Consola o PC, ej: "PS5", "Xbox", "PC", "Switch".
        precio (float): Precio en dolares. Debe ser mayor a 0.
        stock (int): Unidades disponibles. No puede ser negativo.
        descripcion (str): Descripcion detallada del videojuego.

    Raises:
        ValueError: Si el precio es menor o igual a 0.
        ValueError: Si el stock es negativo.
        ValueError: Si el titulo esta vacio.

    Example:
        >>> juego = Videojuego(
        ...     id=None,
        ...     titulo="God of War",
        ...     desarrollador="Santa Monica Studio",
        ...     genero="Accion",
        ...     plataforma="PS5",
        ...     precio=59.99,
        ...     stock=10,
        ...     descripcion="Aventura epica nordica"
        ... )
    """

    id: Optional[int]
    titulo: str
    desarrollador: str
    genero: str
    plataforma: str
    precio: float
    stock: int
    descripcion: str

    def __post_init__(self) -> None:
        """
        Ejecuta las validaciones de negocio al crear el objeto.

        Raises:
            ValueError: Si el precio es <= 0.
            ValueError: Si el stock es negativo.
            ValueError: Si el titulo esta vacio.
        """
        if self.precio <= 0:
            raise ValueError(
                f"El precio debe ser mayor a 0. Precio recibido: {self.precio}"
            )
        if self.stock < 0:
            raise ValueError(
                f"El stock no puede ser negativo. Stock recibido: {self.stock}"
            )
        if not self.titulo or not self.titulo.strip():
            raise ValueError("El titulo del videojuego no puede estar vacio.")

    def tiene_stock(self) -> bool:
        """
        Indica si el videojuego esta disponible para compra.

        Returns:
            bool: True si hay al menos una unidad en inventario.

        Example:
            >>> juego.tiene_stock()
            True
        """
        return self.stock > 0

    def vender(self, cantidad: int) -> None:
        """
        Reduce el inventario al registrar una venta.

        Valida que la cantidad sea positiva y que haya suficiente
        stock antes de descontar las unidades vendidas.

        Args:
            cantidad (int): Numero de unidades vendidas. Debe ser >= 1.

        Raises:
            ValueError: Si la cantidad es menor a 1.
            ValueError: Si el stock disponible es insuficiente.

        Example:
            >>> juego.vender(2)
        """
        if cantidad < 1:
            raise ValueError(
                f"La cantidad vendida debe ser al menos 1. Recibida: {cantidad}"
            )
        if cantidad > self.stock:
            raise ValueError(
                f"Stock insuficiente para '{self.titulo}'. "
                f"Disponible: {self.stock}, solicitado: {cantidad}"
            )
        self.stock -= cantidad

    def reabastecer(self, cantidad: int) -> None:
        """
        Aumenta el inventario del videojuego.

        Se usa cuando llegan nuevas unidades al almacen.

        Args:
            cantidad (int): Unidades a agregar al inventario. Debe ser >= 1.

        Raises:
            ValueError: Si la cantidad es menor a 1.

        Example:
            >>> juego.reabastecer(5)
        """
        if cantidad < 1:
            raise ValueError(
                f"La cantidad a reabastecer debe ser al menos 1. Recibida: {cantidad}"
            )
        self.stock += cantidad


@dataclass
class MensajeChat:
    """
    Entidad que representa un mensaje dentro de una sesion de chat.

    Cada mensaje pertenece a una sesion de conversacion y puede ser
    enviado por el cliente ('usuario') o el asistente de IA ('asistente').

    Attributes:
        id (Optional[int]): Identificador unico del mensaje.
        sesion_id (str): Identificador de la sesion de conversacion.
        rol (str): Quien envio el mensaje: 'usuario' o 'asistente'.
        contenido (str): Texto del mensaje.
        fecha_hora (datetime): Momento en que se envio el mensaje.

    Raises:
        ValueError: Si el rol no es 'usuario' o 'asistente'.
        ValueError: Si el contenido o sesion_id estan vacios.

    Example:
        >>> msg = MensajeChat(
        ...     id=None,
        ...     sesion_id="jugador_001",
        ...     rol="usuario",
        ...     contenido="Busco juegos de RPG para PS5",
        ...     fecha_hora=datetime.utcnow()
        ... )
    """

    id: Optional[int]
    sesion_id: str
    rol: str
    contenido: str
    fecha_hora: datetime

    def __post_init__(self) -> None:
        """
        Valida los campos obligatorios al crear el mensaje.

        Raises:
            ValueError: Si el rol no es valido.
            ValueError: Si el contenido esta vacio.
            ValueError: Si el sesion_id esta vacio.
        """
        roles_validos = {"usuario", "asistente"}
        if self.rol not in roles_validos:
            raise ValueError(
                f"El rol debe ser 'usuario' o 'asistente'. Rol recibido: '{self.rol}'"
            )
        if not self.contenido or not self.contenido.strip():
            raise ValueError("El contenido del mensaje no puede estar vacio.")
        if not self.sesion_id or not self.sesion_id.strip():
            raise ValueError("El sesion_id no puede estar vacio.")

    def es_del_usuario(self) -> bool:
        """
        Indica si el mensaje fue enviado por el cliente.

        Returns:
            bool: True si el rol es 'usuario'.
        """
        return self.rol == "usuario"

    def es_del_asistente(self) -> bool:
        """
        Indica si el mensaje fue enviado por el asistente de IA.

        Returns:
            bool: True si el rol es 'asistente'.
        """
        return self.rol == "asistente"


@dataclass
class ContextoChat:
    """
    Value Object que encapsula el historial reciente de una conversacion.

    Mantiene los ultimos mensajes de una sesion para que el asistente
    de IA recuerde el contexto y genere respuestas coherentes.

    Attributes:
        mensajes (List[MensajeChat]): Lista de mensajes de la sesion.
        max_mensajes (int): Maximo de mensajes a considerar. Por defecto 6.

    Example:
        >>> ctx = ContextoChat(mensajes=historial, max_mensajes=6)
        >>> print(ctx.formatear_para_prompt())
    """

    mensajes: List[MensajeChat]
    max_mensajes: int = 6

    def obtener_recientes(self) -> List[MensajeChat]:
        """
        Retorna los ultimos N mensajes del historial.

        Returns:
            List[MensajeChat]: Los ultimos max_mensajes en orden cronologico.

        Example:
            >>> ctx.obtener_recientes()
            [MensajeChat(...), MensajeChat(...)]
        """
        return self.mensajes[-self.max_mensajes:]

    def formatear_para_prompt(self) -> str:
        """
        Genera un texto con el historial listo para incluir en el prompt de IA.

        Returns:
            str: Historial formateado, ej:
                 "Cliente: Busco RPGs\\nAsistente: Tenemos varios..."

        Example:
            >>> ctx.formatear_para_prompt()
            'Cliente: Busco RPGs para PS5\\nAsistente: Te recomiendo...'
        """
        lineas = []
        for msg in self.obtener_recientes():
            prefijo = "Cliente" if msg.es_del_usuario() else "Asistente"
            lineas.append(f"{prefijo}: {msg.contenido}")
        return "\n".join(lineas)
