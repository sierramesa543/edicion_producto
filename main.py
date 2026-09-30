from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from nucleo.conexion import conexion  # capa 1
from nucleo.configuracion import CONFIGURACION  # capa 1
from presentacion.rutas.productos import router as productos  # capa 3


@asynccontextmanager
async def lifespan(app: FastAPI):
    # main es quien une las piezas: toma la configuración y abre el pool.
    CONFIGURACION.validar()
    await conexion.conectar(CONFIGURACION.base_datos)
    yield
    # Al apagar la aplicación, el pool se cierra para liberar las conexiones.
    await conexion.cerrar()


app = FastAPI(title=CONFIGURACION.nombre_app, lifespan=lifespan)

# Archivos estáticos (CSS) que viven en la capa de presentación.
DIRECTORIO_ESTATICOS = Path(__file__).resolve().parent / "presentacion" / "static"
app.mount("/static", StaticFiles(directory=str(DIRECTORIO_ESTATICOS)), name="static")

app.include_router(productos)


if __name__ == "__main__":
    # Permite arrancar con:  python main.py
    # (también funciona:  uvicorn main:app --reload)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
