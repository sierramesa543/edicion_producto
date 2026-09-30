"""Capa 1 — Conexión. Abre y cierra el pool; entrega conexiones a quien las pida."""
from typing import Annotated, AsyncGenerator

import asyncpg
from fastapi import Depends


class Conexion:
    """Abre y cierra el pool. No sabe qué es un producto."""

    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def conectar(self, url: str) -> None:
        if self.pool is not None:
            return  # ya estaba abierto
        # Un pool: varias conexiones que se reutilizan entre peticiones.
        self.pool = await asyncpg.create_pool(dsn=url)

    async def cerrar(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None


conexion = Conexion()  # una sola instancia para toda la app


async def get_conexion() -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependencia de FastAPI: cede una conexión del pool a cada petición."""
    if conexion.pool is None:
        raise RuntimeError("El pool de conexiones no está abierto.")
    async with conexion.pool.acquire() as conn:
        yield conn


# Así las rutas reciben la conexión de la base de datos como parámetro.
ConexionDep = Annotated[asyncpg.Connection, Depends(get_conexion)]
