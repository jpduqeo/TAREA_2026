"""
Modulo principal de la API REST con FastAPI para GameStore AI.

Define la aplicacion con todos los endpoints, middleware CORS y el
evento de inicio que inicializa la base de datos con el catalogo.
"""

from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.infrastructure.db.base_datos import obtener_sesion, inicializar_bd
from src.infrastructure.repositories.repositorio_videojuegos import RepositorioSQLVideojuegos
from src.infrastructure.repositories.repositorio_chat import RepositorioSQLChat
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.application.servicio_videojuegos import ServicioVideojuegos
from src.application.servicio_chat import ServicioChat
from src.application.dtos import (
    VideojuegoDTO,
    FiltroVideojuegoDTO,
    VentaDTO,
    ResultadoVentaDTO,
    SolicitudChatDTO,
    RespuestaChatDTO,
    HistorialMensajeDTO,
)
from src.domain.excepciones import (
    VideojuegoNoEncontrado,
    DatosVideojuegoInvalidos,
    ErrorServicioChat,
)

app = FastAPI(
    title="GameStore AI - Tienda de Videojuegos con Asistente Inteligente",
    description=(
        "API REST para una tienda de videojuegos con asistente de IA conversacional. "
        "Permite explorar el catalogo, comprar juegos y chatear con GameBot, "
        "un asistente experto en videojuegos potenciado por Google Gemini AI. "
        "Implementado con Clean Architecture en 3 capas."
    ),
    version="1.0.0",
    contact={"name": "Universidad EAFIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def al_iniciar() -> None:
    """
    Evento ejecutado al iniciar la aplicacion.

    Crea las tablas de la base de datos y carga el catalogo
    inicial de videojuegos si la base de datos esta vacia.
    """
    inicializar_bd()


# ─────────────────────────────────────────────
# ENDPOINTS GENERALES
# ─────────────────────────────────────────────

@app.get("/", summary="Informacion de la API", tags=["General"])
def inicio():
    """
    Retorna informacion basica sobre GameStore AI y sus endpoints.

    Returns:
        dict: Nombre, version y lista de endpoints disponibles.

    Example:
        GET /
        Response: {"nombre": "GameStore AI", "version": "1.0.0", ...}
    """
    return {
        "nombre": "GameStore AI",
        "version": "1.0.0",
        "descripcion": "Tienda de videojuegos con asistente IA conversacional",
        "endpoints": {
            "catalogo": "/games",
            "chat": "/chat",
            "documentacion": "/docs",
            "salud": "/health",
        },
    }


@app.get("/health", summary="Estado del servicio", tags=["General"])
def verificar_estado():
    """
    Endpoint de health check para monitoreo del servicio.

    Returns:
        dict: Estado actual y timestamp del sistema.

    Example:
        GET /health
        Response: {"estado": "activo", "timestamp": "..."}
    """
    return {
        "estado": "activo",
        "timestamp": datetime.utcnow().isoformat(),
        "servicio": "GameStore AI API",
    }


# ─────────────────────────────────────────────
# ENDPOINTS DE VIDEOJUEGOS
# ─────────────────────────────────────────────

@app.get(
    "/games",
    response_model=List[VideojuegoDTO],
    summary="Listar catalogo de videojuegos",
    tags=["Videojuegos"],
)
def listar_juegos(
    genero: str = Query(default=None, description="Filtrar por genero: RPG, Accion, Deportes..."),
    plataforma: str = Query(default=None, description="Filtrar por plataforma: PS5, Xbox, PC, Switch"),
    db: Session = Depends(obtener_sesion),
):
    """
    Obtiene el catalogo completo de videojuegos con filtros opcionales.

    Args:
        genero (str, opcional): Genero para filtrar el catalogo.
        plataforma (str, opcional): Plataforma para filtrar el catalogo.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        List[VideojuegoDTO]: Lista de videojuegos que cumplen los filtros.

    Example:
        GET /games
        GET /games?genero=RPG
        GET /games?plataforma=PS5
    """
    repo = RepositorioSQLVideojuegos(sesion=db)
    servicio = ServicioVideojuegos(repositorio=repo)
    filtro = FiltroVideojuegoDTO(genero=genero, plataforma=plataforma)
    return servicio.buscar_con_filtros(filtro)


@app.get(
    "/games/disponibles",
    response_model=List[VideojuegoDTO],
    summary="Listar juegos con stock disponible",
    tags=["Videojuegos"],
)
def listar_juegos_disponibles(db: Session = Depends(obtener_sesion)):
    """
    Retorna unicamente los videojuegos con al menos una unidad en stock.

    Args:
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        List[VideojuegoDTO]: Juegos disponibles para compra inmediata.

    Example:
        GET /games/disponibles
    """
    repo = RepositorioSQLVideojuegos(sesion=db)
    servicio = ServicioVideojuegos(repositorio=repo)
    return servicio.listar_disponibles()


@app.get(
    "/games/{juego_id}",
    response_model=VideojuegoDTO,
    summary="Obtener un videojuego por ID",
    tags=["Videojuegos"],
)
def obtener_juego(juego_id: int, db: Session = Depends(obtener_sesion)):
    """
    Obtiene todos los detalles de un videojuego especifico por su ID.

    Args:
        juego_id (int): Identificador unico del videojuego.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        VideojuegoDTO: Datos completos del videojuego.

    Raises:
        HTTPException(404): Si no existe videojuego con ese ID.

    Example:
        GET /games/1
        Response: {"id": 1, "titulo": "Elden Ring", "precio": 59.99, ...}
    """
    repo = RepositorioSQLVideojuegos(sesion=db)
    servicio = ServicioVideojuegos(repositorio=repo)
    try:
        return servicio.buscar_por_id(juego_id)
    except VideojuegoNoEncontrado as e:
        raise HTTPException(status_code=404, detail=e.mensaje)


@app.post(
    "/games/{juego_id}/comprar",
    response_model=ResultadoVentaDTO,
    summary="Comprar un videojuego (reduce stock)",
    tags=["Videojuegos"],
)
def comprar_juego(
    juego_id: int,
    datos_compra: VentaDTO,
    db: Session = Depends(obtener_sesion),
):
    """
    Procesa la compra de un videojuego reduciendo su stock automaticamente.

    Implementa la regla de negocio del dominio: al vender un videojuego,
    el inventario se reduce de forma inmediata. Valida disponibilidad
    antes de confirmar la transaccion.

    Args:
        juego_id (int): ID del videojuego a comprar.
        datos_compra (VentaDTO): Cuerpo del request con la cantidad a comprar.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        ResultadoVentaDTO: Confirmacion con el stock restante.

    Raises:
        HTTPException(404): Si el videojuego no existe.
        HTTPException(400): Si no hay suficiente stock disponible.

    Example:
        POST /games/1/comprar
        Body: {"cantidad": 1}
        Response: {"titulo": "Elden Ring", "cantidad_vendida": 1, "stock_restante": 14}
    """
    repo = RepositorioSQLVideojuegos(sesion=db)
    servicio = ServicioVideojuegos(repositorio=repo)
    try:
        return servicio.procesar_venta(
            juego_id=juego_id,
            cantidad=datos_compra.cantidad,
        )
    except VideojuegoNoEncontrado as e:
        raise HTTPException(status_code=404, detail=e.mensaje)
    except DatosVideojuegoInvalidos as e:
        raise HTTPException(status_code=400, detail=e.mensaje)


# ─────────────────────────────────────────────
# ENDPOINTS DE CHAT
# ─────────────────────────────────────────────

@app.post(
    "/chat",
    response_model=RespuestaChatDTO,
    summary="Chatear con GameBot (asistente IA)",
    tags=["Chat"],
)
async def chatear(solicitud: SolicitudChatDTO, db: Session = Depends(obtener_sesion)):
    """
    Envia un mensaje a GameBot y recibe una respuesta inteligente.

    GameBot conoce el catalogo completo y recuerda el historial de la
    conversacion por sesion. Usa Google Gemini AI para generar respuestas
    expertas en videojuegos.

    Args:
        solicitud (SolicitudChatDTO): Mensaje del cliente con su sesion_id.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        RespuestaChatDTO: Respuesta de GameBot con timestamp.

    Raises:
        HTTPException(500): Si ocurre un error interno al procesar el mensaje.

    Example:
        POST /chat
        Body: {"sesion_id": "jugador_001", "mensaje": "Busco RPGs para PS5"}
        Response: {
            "sesion_id": "jugador_001",
            "mensaje_usuario": "Busco RPGs para PS5",
            "respuesta_asistente": "En PS5 tenemos God of War Ragnarok...",
            "fecha_hora": "2024-01-15T10:30:00"
        }
    """
    repo_juegos = RepositorioSQLVideojuegos(sesion=db)
    repo_chat = RepositorioSQLChat(sesion=db)
    try:
        ia = GeminiService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    servicio = ServicioChat(
        repositorio_juegos=repo_juegos,
        repositorio_chat=repo_chat,
        servicio_ia=ia,
    )
    try:
        return await servicio.procesar_mensaje(solicitud)
    except ErrorServicioChat as e:
        raise HTTPException(status_code=500, detail=e.mensaje)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


@app.get(
    "/chat/historial/{sesion_id}",
    response_model=List[HistorialMensajeDTO],
    summary="Ver historial de conversacion",
    tags=["Chat"],
)
def ver_historial(
    sesion_id: str,
    limite: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(obtener_sesion),
):
    """
    Recupera el historial de mensajes de una sesion de chat.

    Args:
        sesion_id (str): Identificador de la sesion de conversacion.
        limite (int): Maximo de mensajes a retornar (1-100, defecto 10).
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        List[HistorialMensajeDTO]: Mensajes en orden cronologico.

    Example:
        GET /chat/historial/jugador_001?limite=20
    """
    repo_chat = RepositorioSQLChat(sesion=db)
    mensajes = repo_chat.obtener_historial_sesion(
        sesion_id=sesion_id, limite=limite
    )
    return [
        HistorialMensajeDTO(
            id=m.id,
            rol=m.rol,
            contenido=m.contenido,
            fecha_hora=m.fecha_hora,
        )
        for m in mensajes
    ]


@app.delete(
    "/chat/historial/{sesion_id}",
    summary="Eliminar historial de conversacion",
    tags=["Chat"],
)
def eliminar_historial(sesion_id: str, db: Session = Depends(obtener_sesion)):
    """
    Borra todo el historial de una sesion para reiniciar la conversacion.

    Args:
        sesion_id (str): Sesion cuyo historial se desea eliminar.
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        dict: Confirmacion con la cantidad de mensajes eliminados.

    Example:
        DELETE /chat/historial/jugador_001
        Response: {"mensaje": "Historial eliminado", "mensajes_eliminados": 4}
    """
    repo_chat = RepositorioSQLChat(sesion=db)
    eliminados = repo_chat.eliminar_historial_sesion(sesion_id)
    return {
        "mensaje": f"Historial de la sesion '{sesion_id}' eliminado correctamente.",
        "mensajes_eliminados": eliminados,
    }
