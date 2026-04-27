"""
Modulo para cargar el catalogo inicial de videojuegos.

Inserta 10 videojuegos de ejemplo al iniciar la aplicacion si la
base de datos esta vacia, permitiendo probar el sistema de inmediato.
"""

from sqlalchemy.orm import Session
from src.infrastructure.db.modelos import ModeloVideojuego


def cargar_juegos_ejemplo(sesion: Session) -> None:
    """
    Carga el catalogo inicial de videojuegos si la base de datos esta vacia.

    Verifica si ya existen registros antes de insertar para evitar
    duplicados en reinicios del servidor.

    Args:
        sesion (Session): Sesion activa de SQLAlchemy.

    Example:
        >>> sesion = FabricaSesion()
        >>> cargar_juegos_ejemplo(sesion)
        >>> sesion.close()
    """
    if sesion.query(ModeloVideojuego).count() > 0:
        return

    catalogo_inicial = [
        ModeloVideojuego(
            titulo="Elden Ring",
            desarrollador="FromSoftware",
            genero="RPG",
            plataforma="PC",
            precio=59.99,
            stock=15,
            descripcion=(
                "RPG de mundo abierto desarrollado junto a George R.R. Martin. "
                "Explora Las Tierras Intermedias en una aventura epica llena de "
                "desafios y lore profundo."
            ),
        ),
        ModeloVideojuego(
            titulo="God of War Ragnarok",
            desarrollador="Santa Monica Studio",
            genero="Accion",
            plataforma="PS5",
            precio=69.99,
            stock=8,
            descripcion=(
                "Kratos y Atreus enfrentan el Ragnarok norreno. Combate brutal "
                "y cinematico combinado con una narrativa emotiva sobre paternidad "
                "y destino."
            ),
        ),
        ModeloVideojuego(
            titulo="The Legend of Zelda: Tears of the Kingdom",
            desarrollador="Nintendo",
            genero="Aventura",
            plataforma="Switch",
            precio=59.99,
            stock=12,
            descripcion=(
                "Link explora Hyrule en una nueva aventura con mecanicas de "
                "construccion y creatividad sin limites. Continuacion directa "
                "de Breath of the Wild."
            ),
        ),
        ModeloVideojuego(
            titulo="Cyberpunk 2077: Phantom Liberty",
            desarrollador="CD Projekt Red",
            genero="RPG",
            plataforma="PC",
            precio=29.99,
            stock=20,
            descripcion=(
                "Expansion de Cyberpunk 2077 ambientada en Dogtown. V se "
                "adentra en el mundo del espionaje corporativo en Night City "
                "con una historia de thriller politico."
            ),
        ),
        ModeloVideojuego(
            titulo="FIFA 24",
            desarrollador="EA Sports",
            genero="Deportes",
            plataforma="Xbox",
            precio=49.99,
            stock=25,
            descripcion=(
                "La entrega anual del simulador de futbol mas popular del mundo. "
                "Incluye Ultimate Team, carrera, y el nuevo modo Clubs mejorado."
            ),
        ),
        ModeloVideojuego(
            titulo="Hollow Knight: Silksong",
            desarrollador="Team Cherry",
            genero="Plataformas",
            plataforma="PC",
            precio=19.99,
            stock=30,
            descripcion=(
                "Secuela de Hollow Knight. Controla a Hornet en un nuevo reino "
                "plagado de enemigos y secretos. Accion precisa con un mundo "
                "oscuro de insectos."
            ),
        ),
        ModeloVideojuego(
            titulo="Spider-Man 2",
            desarrollador="Insomniac Games",
            genero="Accion",
            plataforma="PS5",
            precio=69.99,
            stock=6,
            descripcion=(
                "Peter Parker y Miles Morales se unen para enfrentar a Venom "
                "en Nueva York. Graficos espectaculares y combate fluido en "
                "mundo abierto."
            ),
        ),
        ModeloVideojuego(
            titulo="Baldur's Gate 3",
            desarrollador="Larian Studios",
            genero="RPG",
            plataforma="PC",
            precio=59.99,
            stock=18,
            descripcion=(
                "RPG por turnos basado en D&D 5a edicion. Libertad total de "
                "eleccion en una historia epica con cooperativo de hasta 4 "
                "jugadores."
            ),
        ),
        ModeloVideojuego(
            titulo="Forza Horizon 5",
            desarrollador="Playground Games",
            genero="Carreras",
            plataforma="Xbox",
            precio=39.99,
            stock=14,
            descripcion=(
                "El juego de carreras en mundo abierto ambientado en Mexico. "
                "Mas de 500 autos, clima dinamico y eventos multijugador en "
                "un mapa enorme y detallado."
            ),
        ),
        ModeloVideojuego(
            titulo="Hades II",
            desarrollador="Supergiant Games",
            genero="Roguelike",
            plataforma="PC",
            precio=24.99,
            stock=22,
            descripcion=(
                "Secuela del aclamado roguelike. Controla a Melinoe en su "
                "descenso al inframundo con nuevas armas, habilidades y "
                "personajes de la mitologia griega."
            ),
        ),
    ]

    sesion.add_all(catalogo_inicial)
    sesion.commit()
