"""
Modulo del servicio de IA usando Google Gemini.

Integra la API de Google Gemini para generar respuestas inteligentes
del asistente virtual de la tienda de videojuegos. Incluye fallback
automatico entre modelos si uno falla por cuota.
"""

import os
from typing import List

import google.generativeai as genai

from src.domain.entidades import Videojuego, ContextoChat

MODELOS_DISPONIBLES = [
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
]


class GeminiService:
    """
    Servicio de IA que usa Google Gemini para el asistente de GameStore.

    Genera respuestas inteligentes y contextualizadas sobre el catalogo
    de videojuegos. Si un modelo falla por cuota, intenta automaticamente
    con el siguiente de la lista MODELOS_DISPONIBLES.

    Attributes:
        api_key (str): API Key de Google Gemini leida del entorno.
        modelo_activo (str): Modelo de Gemini actualmente en uso.

    Example:
        >>> ia = GeminiService()
        >>> respuesta = await ia.generar_respuesta(
        ...     mensaje_usuario="Busco RPGs para PC",
        ...     catalogo=lista_juegos,
        ...     contexto=ctx
        ... )
    """

    def __init__(self) -> None:
        """
        Inicializa el servicio configurando el cliente de Gemini.

        Raises:
            ValueError: Si GEMINI_API_KEY no esta definida en el entorno.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY no esta configurada. "
                "Obtenla en https://aistudio.google.com/app/apikey "
                "y agregala al archivo .env"
            )
        genai.configure(api_key=self.api_key)
        self.modelo_activo = MODELOS_DISPONIBLES[0]

    async def generar_respuesta(
        self,
        mensaje_usuario: str,
        catalogo: List[Videojuego],
        contexto: ContextoChat,
    ) -> str:
        """
        Genera una respuesta inteligente sobre videojuegos usando Gemini.

        Construye un prompt con el catalogo y el historial de la conversacion,
        luego consulta a Gemini. Si el modelo falla por cuota, prueba el siguiente
        de la lista automaticamente.

        Args:
            mensaje_usuario (str): Mensaje actual del cliente.
            catalogo (List[Videojuego]): Lista de videojuegos disponibles.
            contexto (ContextoChat): Historial reciente de la conversacion.

        Returns:
            str: Respuesta generada por Gemini AI.

        Raises:
            Exception: Si todos los modelos disponibles fallan.

        Example:
            >>> resp = await ia.generar_respuesta(
            ...     "Que RPGs tienen para PC?", juegos, ctx
            ... )
        """
        info_catalogo = self._formatear_catalogo(catalogo)
        historial = contexto.formatear_para_prompt()
        prompt = self._construir_prompt(mensaje_usuario, info_catalogo, historial)

        ultimo_error = None
        for nombre_modelo in MODELOS_DISPONIBLES:
            try:
                modelo = genai.GenerativeModel(nombre_modelo)
                respuesta = modelo.generate_content(prompt)
                self.modelo_activo = nombre_modelo
                return respuesta.text
            except Exception as e:
                error_str = str(e)
                if any(c in error_str for c in ["429", "404", "quota"]):
                    ultimo_error = e
                    continue
                raise e

        raise Exception(
            f"Todos los modelos de Gemini fallaron. Ultimo error: {ultimo_error}. "
            f"Verifica tu API key en https://aistudio.google.com/app/apikey"
        )

    def _formatear_catalogo(self, catalogo: List[Videojuego]) -> str:
        """
        Convierte el catalogo de videojuegos a texto para el prompt.

        Args:
            catalogo (List[Videojuego]): Juegos a formatear.

        Returns:
            str: Catalogo en formato legible para el modelo de IA.
                 Formato: "- Titulo | Desarrollador | Genero | Plataforma | $Precio | Stock: N"

        Example:
            >>> ia._formatear_catalogo(juegos)
            '- Elden Ring | FromSoftware | RPG | PC | $59.99 | Stock: 15'
        """
        if not catalogo:
            return "No hay videojuegos disponibles en este momento."

        lineas = []
        for j in catalogo:
            disponibilidad = f"Stock: {j.stock}" if j.tiene_stock() else "Agotado"
            lineas.append(
                f"- {j.titulo} | {j.desarrollador} | {j.genero} | "
                f"{j.plataforma} | ${j.precio:.2f} | {disponibilidad}"
            )
        return "\n".join(lineas)

    def _construir_prompt(
        self, mensaje: str, catalogo_txt: str, historial: str
    ) -> str:
        """
        Construye el prompt completo para enviar a Gemini.

        Combina las instrucciones del sistema, el catalogo de juegos,
        el historial y el mensaje actual en un prompt estructurado.

        Args:
            mensaje (str): Mensaje actual del cliente.
            catalogo_txt (str): Catalogo formateado en texto.
            historial (str): Historial de la conversacion formateado.

        Returns:
            str: Prompt completo listo para Gemini.
        """
        seccion_historial = ""
        if historial:
            seccion_historial = f"\nCONVERSACION ANTERIOR:\n{historial}\n"

        return f"""Eres GameBot, el asistente virtual experto en videojuegos de GameStore AI.
Tu mision es ayudar a los clientes a encontrar los videojuegos perfectos segun sus gustos.

CATALOGO DISPONIBLE EN TIENDA:
{catalogo_txt}

INSTRUCCIONES:
- Responde siempre en espanol, con entusiasmo y conocimiento gamer
- Usa el historial para dar respuestas coherentes y contextualizadas
- Recomienda juegos especificos del catalogo cuando sea relevante
- Menciona titulo, genero, plataforma, precio y disponibilidad al recomendar
- Si preguntan por algo no disponible, sugiere alternativas del catalogo
- Manten respuestas concisas (maximo 3 parrafos)
- Si un juego esta agotado, indicalo y ofrece alternativas similares
{seccion_historial}
MENSAJE DEL CLIENTE:
{mensaje}

RESPUESTA DE GAMEBOT:"""
