"""
Tests unitarios para las entidades del dominio de GameStore AI.

Verifica que Videojuego, MensajeChat y ContextoChat cumplan
correctamente las reglas de negocio definidas.
"""

import pytest
from datetime import datetime
from src.domain.entidades import Videojuego, MensajeChat, ContextoChat


class TestVideojuego:
    """Tests unitarios para la entidad Videojuego."""

    def test_crear_juego_valido(self, juego_con_stock):
        """Verifica que se cree correctamente un juego con datos validos."""
        assert juego_con_stock.titulo == "Elden Ring"
        assert juego_con_stock.precio == 59.99
        assert juego_con_stock.stock == 10

    def test_precio_cero_lanza_error(self):
        """Verifica que precio <= 0 lance ValueError."""
        with pytest.raises(ValueError, match="precio"):
            Videojuego(
                id=None, titulo="Test", desarrollador="Dev",
                genero="RPG", plataforma="PC",
                precio=0.0, stock=5, descripcion="test",
            )

    def test_precio_negativo_lanza_error(self):
        """Verifica que precio negativo lance ValueError."""
        with pytest.raises(ValueError):
            Videojuego(
                id=None, titulo="Test", desarrollador="Dev",
                genero="RPG", plataforma="PC",
                precio=-10.0, stock=5, descripcion="test",
            )

    def test_stock_negativo_lanza_error(self):
        """Verifica que stock negativo lance ValueError."""
        with pytest.raises(ValueError, match="stock"):
            Videojuego(
                id=None, titulo="Test", desarrollador="Dev",
                genero="RPG", plataforma="PC",
                precio=50.0, stock=-1, descripcion="test",
            )

    def test_titulo_vacio_lanza_error(self):
        """Verifica que titulo vacio lance ValueError."""
        with pytest.raises(ValueError, match="titulo"):
            Videojuego(
                id=None, titulo="", desarrollador="Dev",
                genero="RPG", plataforma="PC",
                precio=50.0, stock=5, descripcion="test",
            )

    def test_tiene_stock_con_unidades(self, juego_con_stock):
        """Verifica que tiene_stock() retorne True con stock > 0."""
        assert juego_con_stock.tiene_stock() is True

    def test_tiene_stock_sin_unidades(self, juego_sin_stock):
        """Verifica que tiene_stock() retorne False con stock = 0."""
        assert juego_sin_stock.tiene_stock() is False

    def test_vender_reduce_stock_correctamente(self, juego_con_stock):
        """Verifica que vender() descuente las unidades del stock."""
        stock_inicial = juego_con_stock.stock
        juego_con_stock.vender(3)
        assert juego_con_stock.stock == stock_inicial - 3

    def test_vender_mas_del_stock_lanza_error(self, juego_con_stock):
        """Verifica que vender mas del stock disponible lance ValueError."""
        with pytest.raises(ValueError, match="Stock insuficiente"):
            juego_con_stock.vender(100)

    def test_vender_cantidad_cero_lanza_error(self, juego_con_stock):
        """Verifica que vender 0 unidades lance ValueError."""
        with pytest.raises(ValueError):
            juego_con_stock.vender(0)

    def test_reabastecer_aumenta_stock(self, juego_con_stock):
        """Verifica que reabastecer() aumente el stock correctamente."""
        stock_inicial = juego_con_stock.stock
        juego_con_stock.reabastecer(5)
        assert juego_con_stock.stock == stock_inicial + 5

    def test_reabastecer_cantidad_invalida_lanza_error(self, juego_con_stock):
        """Verifica que reabastecer con cantidad <= 0 lance ValueError."""
        with pytest.raises(ValueError):
            juego_con_stock.reabastecer(0)

    def test_stock_puede_ser_cero(self):
        """Verifica que se pueda crear un juego agotado (stock = 0)."""
        juego = Videojuego(
            id=None, titulo="Juego Agotado", desarrollador="Dev",
            genero="Accion", plataforma="Xbox",
            precio=49.99, stock=0, descripcion="Agotado",
        )
        assert juego.stock == 0
        assert juego.tiene_stock() is False


class TestMensajeChat:
    """Tests unitarios para la entidad MensajeChat."""

    def test_crear_mensaje_usuario_valido(self, mensaje_cliente):
        """Verifica que se cree un mensaje de cliente correctamente."""
        assert mensaje_cliente.rol == "usuario"
        assert len(mensaje_cliente.contenido) > 0

    def test_crear_mensaje_asistente_valido(self, mensaje_asistente):
        """Verifica que se cree un mensaje de asistente correctamente."""
        assert mensaje_asistente.rol == "asistente"

    def test_rol_invalido_lanza_error(self):
        """Verifica que un rol distinto a usuario/asistente lance ValueError."""
        with pytest.raises(ValueError, match="rol"):
            MensajeChat(
                id=None, sesion_id="s1", rol="admin",
                contenido="Hola", fecha_hora=datetime.utcnow(),
            )

    def test_contenido_vacio_lanza_error(self):
        """Verifica que contenido vacio lance ValueError."""
        with pytest.raises(ValueError, match="contenido"):
            MensajeChat(
                id=None, sesion_id="s1", rol="usuario",
                contenido="", fecha_hora=datetime.utcnow(),
            )

    def test_sesion_id_vacio_lanza_error(self):
        """Verifica que sesion_id vacio lance ValueError."""
        with pytest.raises(ValueError, match="sesion_id"):
            MensajeChat(
                id=None, sesion_id="", rol="usuario",
                contenido="Hola", fecha_hora=datetime.utcnow(),
            )

    def test_es_del_usuario(self, mensaje_cliente):
        """Verifica que es_del_usuario() retorne True para mensajes del cliente."""
        assert mensaje_cliente.es_del_usuario() is True
        assert mensaje_cliente.es_del_asistente() is False

    def test_es_del_asistente(self, mensaje_asistente):
        """Verifica que es_del_asistente() retorne True para el asistente."""
        assert mensaje_asistente.es_del_asistente() is True
        assert mensaje_asistente.es_del_usuario() is False


class TestContextoChat:
    """Tests unitarios para el Value Object ContextoChat."""

    def test_obtener_recientes_limita_mensajes(self):
        """Verifica que obtener_recientes() retorne solo los ultimos N mensajes."""
        mensajes = [
            MensajeChat(
                id=i, sesion_id="s1", rol="usuario",
                contenido=f"Mensaje {i}", fecha_hora=datetime.utcnow()
            )
            for i in range(1, 10)
        ]
        ctx = ContextoChat(mensajes=mensajes, max_mensajes=3)
        recientes = ctx.obtener_recientes()
        assert len(recientes) == 3
        assert recientes[-1].contenido == "Mensaje 9"

    def test_formatear_para_prompt_formato_correcto(self, contexto_test):
        """Verifica que formatear_para_prompt() genere el formato esperado."""
        texto = contexto_test.formatear_para_prompt()
        assert "Cliente:" in texto
        assert "Asistente:" in texto
        assert "RPG" in texto

    def test_formatear_prompt_vacio_retorna_string_vacio(self):
        """Verifica que un contexto sin mensajes retorne string vacio."""
        ctx = ContextoChat(mensajes=[])
        assert ctx.formatear_para_prompt() == ""

    def test_max_mensajes_por_defecto(self):
        """Verifica que el valor por defecto de max_mensajes sea 6."""
        ctx = ContextoChat(mensajes=[])
        assert ctx.max_mensajes == 6
