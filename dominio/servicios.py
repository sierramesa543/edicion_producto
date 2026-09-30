"""Reglas de la tienda.

Aquí vive lo que la aplicación sabe hacer. No sabe de HTTP,
no sabe de plantillas y no abre conexiones: las recibe.
"""
from dominio import repositorios


class ProductoNoEncontrado(Exception):
    """Regla violada: el producto pedido no existe."""


async def listar_productos(conn) -> list[dict]:
    """Todos los productos, ordenados por nombre."""
    return await repositorios.obtener_productos(conn)


async def obtener_producto(conn, producto_id: int) -> dict:
    """Devuelve el producto o lanza ProductoNoEncontrado."""
    producto = await repositorios.obtener_producto(conn, producto_id)
    if producto is None:
        raise ProductoNoEncontrado(producto_id)
    return producto


async def guardar_cambios(
    conn,
    producto_id: int,
    nombre: str,
    precio: float,
    cantidad: int,
    descripcion: str | None,
) -> None:
    """Actualiza un producto. REGLA: solo se puede editar uno que exista."""
    actualizado = await repositorios.actualizar_producto(
        conn, producto_id, nombre, precio, cantidad, descripcion
    )
    if not actualizado:
        raise ProductoNoEncontrado(producto_id)


async def borrar_producto(conn, producto_id: int) -> None:
    """Elimina un producto. REGLA: solo se puede borrar uno que exista."""
    eliminado = await repositorios.eliminar_producto(conn, producto_id)
    if not eliminado:
        raise ProductoNoEncontrado(producto_id)
