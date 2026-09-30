"""Capa 1 — Configuración: lo único que llega de afuera del código."""
import os

from dotenv import load_dotenv

# Lee el archivo .env (si existe) y carga sus variables en el entorno.
load_dotenv()


class Configuracion:
    """Se lee una sola vez, al arrancar. El resto del proyecto no toca os.environ."""

    def __init__(self) -> None:
        self.base_datos: str = os.environ.get("DATABASE_URL", "")
        self.nombre_app: str = "Productos"

    def validar(self) -> None:
        """Falla con un mensaje claro si falta la cadena de conexión."""
        if not self.base_datos:
            raise RuntimeError(
                "Falta la variable DATABASE_URL. Crea un archivo .env junto a "
                "main.py con la línea: "
                "DATABASE_URL=postgresql://usuario:contrasena@host:puerto/basedatos"
            )


CONFIGURACION = Configuracion()
