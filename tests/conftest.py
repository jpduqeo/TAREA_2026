"""
Configuracion de pytest con fixtures compartidos para GameStore AI.

Los fixtures aqui definidos estan disponibles en todos los tests
sin necesidad de importarlos explicitamente.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock
from typing import List

from src.domain.entidades import Videojuego, MensajeChat, ContextoChat
from src.domain.repositorios import IRepositorioVideojuegos, IRepositorioChat


@pytest.fixture
def juego_con_stock() -> Videojuego:
    """
    Crea un videojuego con stock disponible para tests.

    Returns:
        Videojuego: Juego con stock = 10.
    """
    return Videojuego(
        id=1,
        titulo="Elden Ring",
        desarrollador="FromSoftware",
        genero="RPG",
        plataforma="PC",
        precio=59.99,
        stock=10,
        descripcion="RPG de mundo abierto.",
    )


@pytest.fixture
def juego_sin_stock() -> Videojuego:
    """
    Crea un videojuego sin stock para tests de disponibilidad.

    Returns:
        Videojuego: Juego con stock = 0.
    """
    return Videojuego(
        id=2,
        titulo="God of War Ragnarok",
        desarrollador="Santa Monica Studio",
        genero="Accion",
        plataforma="PS5",
        precio=69.99,
        stock=0,
        descripcion="Aventura nordica epica.",
    )


@pytest.fixture
def lista_juegos(juego_con_stock, juego_sin_stock) -> List[Videojuego]:
    """
    Lista de videojuegos de prueba.

    Returns:
        List[Videojuego]: Dos juegos (uno con stock, uno sin).
    """
    return [juego_con_stock, juego_sin_stock]


@pytest.fixture
def mensaje_cliente() -> MensajeChat:
    """
    Crea un mensaje de cliente para tests de chat.

    Returns:
        MensajeChat: Mensaje con rol 'usuario'.
    """
    return MensajeChat(
        id=1,
        sesion_id="sesion_test",
        rol="usuario",
        contenido="Busco juegos de RPG para PC",
        fecha_hora=datetime(2024, 3, 15, 10, 0, 0),
    )


@pytest.fixture
def mensaje_asistente() -> MensajeChat:
    """
    Crea un mensaje del asistente para tests de chat.

    Returns:
        MensajeChat: Mensaje con rol 'asistente'.
    """
    return MensajeChat(
        id=2,
        sesion_id="sesion_test",
        rol="asistente",
        contenido="Tenemos Elden Ring y Baldur's Gate 3 disponibles.",
        fecha_hora=datetime(2024, 3, 15, 10, 0, 2),
    )


@pytest.fixture
def contexto_test(mensaje_cliente, mensaje_asistente) -> ContextoChat:
    """
    Crea un contexto de chat con mensajes de prueba.

    Returns:
        ContextoChat: Contexto con 2 mensajes.
    """
    return ContextoChat(
        mensajes=[mensaje_cliente, mensaje_asistente],
        max_mensajes=6,
    )


@pytest.fixture
def mock_repo_juegos(lista_juegos) -> MagicMock:
    """
    Mock del repositorio de videojuegos con datos precargados.

    Returns:
        MagicMock: Mock configurado de IRepositorioVideojuegos.
    """
    repo = MagicMock(spec=IRepositorioVideojuegos)
    repo.obtener_todos.return_value = lista_juegos
    repo.obtener_por_id.side_effect = lambda jid: next(
        (j for j in lista_juegos if j.id == jid), None
    )
    repo.obtener_por_genero.side_effect = lambda g: [
        j for j in lista_juegos if g.lower() in j.genero.lower()
    ]
    repo.obtener_por_plataforma.side_effect = lambda p: [
        j for j in lista_juegos if p.lower() in j.plataforma.lower()
    ]
    repo.guardar.side_effect = lambda j: j
    repo.eliminar.return_value = True
    return repo


@pytest.fixture
def mock_repo_chat(mensaje_cliente, mensaje_asistente) -> MagicMock:
    """
    Mock del repositorio de chat con mensajes de prueba.

    Returns:
        MagicMock: Mock configurado de IRepositorioChat.
    """
    repo = MagicMock(spec=IRepositorioChat)
    repo.guardar_mensaje.side_effect = lambda m: m
    repo.obtener_historial_sesion.return_value = [mensaje_cliente, mensaje_asistente]
    repo.obtener_mensajes_recientes.return_value = [mensaje_cliente, mensaje_asistente]
    repo.eliminar_historial_sesion.return_value = 2
    return repo
