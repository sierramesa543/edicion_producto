"""Capa 2 — Acceso a datos: el único archivo del proyecto con SQL.

Todas las consultas usan parámetros ($1, $2, ...): nunca se concatenan
valores recibidos del formulario dentro del texto SQL.
"""


async def obtener_productos(conn) -> list[dict]:
    """Devuelve todos los productos, ordenados por nombre."""
    filas = await conn.fetch(
        """
        SELECT id, nombre, precio, cantidad, descripcion
          FROM productos
         ORDER BY nombre
        """
    )
    # asyncpg devuelve objetos Record; los pasamos a dict para que Jinja2
    # pueda leerlos con producto.nombre, producto.precio, etc.
    return [dict(fila) for fila in filas]


async def obtener_producto(conn, producto_id: int) -> dict | None:
    """Busca un producto por su clave primaria (id)."""
    fila = await conn.fetchrow(
        """
        SELECT id, nombre, precio, cantidad, descripcion
          FROM productos
         WHERE id = $1
        """,
        producto_id,
    )
    # fetchrow devuelve None cuando no hay ninguna fila con ese id.
    return dict(fila) if fila is not None else None


async def actualizar_producto(
    conn,
    producto_id: int,
    nombre: str,
    precio: float,
    cantidad: int,
    descripcion: str | None,
) -> bool:
    """Actualiza un producto. Devuelve True si modificó una fila."""
    resultado = await conn.execute(
        """
        UPDATE productos
           SET nombre = $2, precio = $3, cantidad = $4, descripcion = $5
         WHERE id = $1
        """,
        producto_id,
        nombre,
        precio,
        cantidad,
        descripcion,
    )
    # asyncpg devuelve "UPDATE 1" si modificó una fila ("UPDATE 0" si no existía).
    return resultado == "UPDATE 1"


async def eliminar_producto(conn, producto_id: int) -> bool:
    """Elimina un producto. Devuelve True si borró una fila."""
    resultado = await conn.execute(
        """
        DELETE FROM productos
         WHERE id = $1
        """,
        producto_id,
    )
    # "DELETE 1" significa que se borró una fila.
    return resultado == "DELETE 1"
