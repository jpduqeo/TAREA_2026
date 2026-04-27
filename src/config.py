"""
Modulo de configuracion global de GameStore AI.
Lee variables de entorno para configurar la aplicacion.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Configuracion:
    """
    Configuracion global leida desde variables de entorno.

    Attributes:
        gemini_api_key (str): API Key de Google Gemini.
        url_base_datos (str): URL de conexion a la base de datos.
        entorno (str): Entorno de ejecucion (development/production).
    """
    def __init__(self) -> None:
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.url_base_datos: str = os.getenv("DATABASE_URL", "sqlite:///./data/gamestore.db")
        self.entorno: str = os.getenv("ENVIRONMENT", "development")

    @property
    def es_desarrollo(self) -> bool:
        """Indica si la aplicacion corre en modo desarrollo."""
        return self.entorno == "development"

configuracion = Configuracion()
