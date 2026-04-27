"""
Tests unitarios para los servicios de la capa de aplicacion.

Verifica ServicioVideojuegos y ServicioChat usando mocks de repositorios
para aislar la logica de negocio de la base de datos.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.servicio_videojuegos import ServicioVideojuegos
from src.application.servicio_chat import ServicioChat
from src.application.dtos import VideojuegoDTO, SolicitudChatDTO, FiltroVideojuegoDTO
from src.domain.excepciones import VideojuegoNoEncontrado, DatosVideojuegoInvalidos


class TestServicioVideojuegos:
    """Tests unitarios para el servicio de videojuegos."""

    def test_listar_catalogo_retorna_todos(self, mock_repo_juegos, lista_juegos):
        """Verifica que listar_catalogo() retorne todos los juegos como DTOs."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        resultado = servicio.listar_catalogo()
        assert len(resultado) == len(lista_juegos)
        mock_repo_juegos.obtener_todos.assert_called_once()

    def test_listar_catalogo_retorna_dtos(self, mock_repo_juegos):
        """Verifica que los elementos retornados sean instancias de VideojuegoDTO."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        for item in servicio.listar_catalogo():
            assert isinstance(item, VideojuegoDTO)

    def test_buscar_por_id_existente(self, mock_repo_juegos, juego_con_stock):
        """Verifica que buscar_por_id() retorne el juego correcto."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        resultado = servicio.buscar_por_id(1)
        assert resultado.titulo == juego_con_stock.titulo

    def test_buscar_por_id_inexistente_lanza_error(self, mock_repo_juegos):
        """Verifica que buscar_por_id() lance error si el juego no existe."""
        mock_repo_juegos.obtener_por_id.return_value = None
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        with pytest.raises(VideojuegoNoEncontrado):
            servicio.buscar_por_id(9999)

    def test_buscar_con_filtro_genero(self, mock_repo_juegos):
        """Verifica que se filtre correctamente por genero."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        filtro = FiltroVideojuegoDTO(genero="RPG")
        servicio.buscar_con_filtros(filtro)
        mock_repo_juegos.obtener_por_genero.assert_called_once_with("RPG")

    def test_buscar_con_filtro_plataforma(self, mock_repo_juegos):
        """Verifica que se filtre correctamente por plataforma."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        filtro = FiltroVideojuegoDTO(plataforma="PS5")
        servicio.buscar_con_filtros(filtro)
        mock_repo_juegos.obtener_por_plataforma.assert_called_once_with("PS5")

    def test_buscar_sin_filtros_retorna_todos(self, mock_repo_juegos):
        """Verifica que sin filtros se retorne el catalogo completo."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        servicio.buscar_con_filtros(FiltroVideojuegoDTO())
        mock_repo_juegos.obtener_todos.assert_called_once()

    def test_listar_disponibles_excluye_sin_stock(self, mock_repo_juegos):
        """Verifica que solo se retornen juegos con stock > 0."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        resultado = servicio.listar_disponibles()
        for j in resultado:
            assert j.stock > 0

    def test_eliminar_juego_existente(self, mock_repo_juegos):
        """Verifica que eliminar_juego() llame al repositorio correctamente."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        assert servicio.eliminar_juego(1) is True
        mock_repo_juegos.eliminar.assert_called_once_with(1)

    def test_eliminar_juego_inexistente_lanza_error(self, mock_repo_juegos):
        """Verifica que eliminar un juego inexistente lance error."""
        mock_repo_juegos.obtener_por_id.return_value = None
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        with pytest.raises(VideojuegoNoEncontrado):
            servicio.eliminar_juego(9999)

    def test_procesar_venta_reduce_stock(self, mock_repo_juegos, juego_con_stock):
        """Verifica que la venta reduzca el stock correctamente."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        stock_inicial = juego_con_stock.stock
        resultado = servicio.procesar_venta(juego_id=1, cantidad=3)
        assert resultado.cantidad_vendida == 3
        assert resultado.stock_restante == stock_inicial - 3
        mock_repo_juegos.guardar.assert_called_once()

    def test_procesar_venta_juego_inexistente(self, mock_repo_juegos):
        """Verifica que vender un juego inexistente lance error."""
        mock_repo_juegos.obtener_por_id.return_value = None
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        with pytest.raises(VideojuegoNoEncontrado):
            servicio.procesar_venta(juego_id=9999, cantidad=1)

    def test_procesar_venta_stock_insuficiente(self, mock_repo_juegos):
        """Verifica que vender mas del stock disponible lance error."""
        servicio = ServicioVideojuegos(repositorio=mock_repo_juegos)
        with pytest.raises(DatosVideojuegoInvalidos):
            servicio.procesar_venta(juego_id=1, cantidad=9999)


class TestServicioChat:
    """Tests unitarios para el servicio de chat."""

    def test_obtener_historial_retorna_mensajes(self, mock_repo_juegos, mock_repo_chat):
        """Verifica que obtener_historial() retorne el historial de la sesion."""
        ia = MagicMock()
        servicio = ServicioChat(
            repositorio_juegos=mock_repo_juegos,
            repositorio_chat=mock_repo_chat,
            servicio_ia=ia,
        )
        historial = servicio.obtener_historial("sesion_test", limite=10)
        assert len(historial) == 2

    def test_limpiar_sesion_retorna_cantidad(self, mock_repo_juegos, mock_repo_chat):
        """Verifica que limpiar_sesion() retorne el numero de mensajes eliminados."""
        ia = MagicMock()
        servicio = ServicioChat(
            repositorio_juegos=mock_repo_juegos,
            repositorio_chat=mock_repo_chat,
            servicio_ia=ia,
        )
        assert servicio.limpiar_sesion("sesion_test") == 2

    @pytest.mark.asyncio
    async def test_procesar_mensaje_llama_a_ia(self, mock_repo_juegos, mock_repo_chat):
        """Verifica que procesar_mensaje() llame al servicio de IA."""
        ia = MagicMock()
        ia.generar_respuesta = AsyncMock(
            return_value="Tenemos Elden Ring disponible en PC por $59.99."
        )
        servicio = ServicioChat(
            repositorio_juegos=mock_repo_juegos,
            repositorio_chat=mock_repo_chat,
            servicio_ia=ia,
        )
        solicitud = SolicitudChatDTO(sesion_id="sesion_test", mensaje="Busco RPGs")
        respuesta = await servicio.procesar_mensaje(solicitud)

        ia.generar_respuesta.assert_called_once()
        assert respuesta.sesion_id == "sesion_test"
        assert "Elden Ring" in respuesta.respuesta_asistente

    @pytest.mark.asyncio
    async def test_procesar_mensaje_guarda_dos_mensajes(
        self, mock_repo_juegos, mock_repo_chat
    ):
        """Verifica que se persistan el mensaje del cliente y la respuesta del asistente."""
        ia = MagicMock()
        ia.generar_respuesta = AsyncMock(return_value="Respuesta de prueba.")
        servicio = ServicioChat(
            repositorio_juegos=mock_repo_juegos,
            repositorio_chat=mock_repo_chat,
            servicio_ia=ia,
        )
        solicitud = SolicitudChatDTO(sesion_id="sesion_test", mensaje="Hola")
        await servicio.procesar_mensaje(solicitud)
        assert mock_repo_chat.guardar_mensaje.call_count == 2
