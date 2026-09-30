"""Capa 3 — Rutas del módulo productos: recibe, delega y elige plantilla."""
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from dominio.esquemas import ProductoActualizar
from dominio.servicios import (
    ProductoNoEncontrado,
    borrar_producto,
    guardar_cambios,
    listar_productos,
    obtener_producto,
)
from nucleo.conexion import ConexionDep

router = APIRouter(tags=["productos"])

# Ruta absoluta a presentacion/templates: funciona sin importar desde
# qué carpeta se ejecute el servidor.
DIRECTORIO_PLANTILLAS = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(DIRECTORIO_PLANTILLAS))

# Mensajes que se muestran debajo de cada campo cuando la validación falla.
# Son mensajes para personas, no los mensajes técnicos de Pydantic.
MENSAJES_ERROR = {
    "nombre": "El nombre es obligatorio (entre 1 y 100 caracteres).",
    "precio": "El precio debe ser un número mayor que cero.",
    "cantidad": "La cantidad debe ser un número entero mayor o igual que cero.",
}


def producto_no_encontrado(request: Request, producto_id: int):
    """Fragmento que HTMX coloca en lugar de la fila cuando el id no existe.

    Se responde con el código 404 (no encontrado) y NO con un mensaje de
    éxito: así la interfaz nunca miente sobre el resultado de la operación.
    """
    return templates.TemplateResponse(
        request=request,
        name="componentes/producto_no_encontrado.html",
        context={"producto_id": producto_id},
        status_code=404,
    )


def errores_de_validacion(exc: ValidationError) -> dict[str, str]:
    """Traduce los errores de Pydantic a un mensaje comprensible por campo."""
    errores: dict[str, str] = {}
    for error in exc.errors():
        campo = str(error["loc"][0])
        if campo not in errores:
            errores[campo] = MENSAJES_ERROR.get(campo, "Valor inválido.")
    return errores


@router.get("/", include_in_schema=False)
async def inicio():
    # La página de inicio lleva directamente a la lista de productos.
    return RedirectResponse(url="/productos")


@router.get("/productos")
async def listar_productos_vista(request: Request, conn: ConexionDep):
    productos = await listar_productos(conn)
    return templates.TemplateResponse(
        request=request,
        name="productos.html",
        context={"productos": productos},
    )


@router.get("/productos/{producto_id}/editar")
async def editar_producto_vista(request: Request, conn: ConexionDep, producto_id: int):
    try:
        producto = await obtener_producto(conn, producto_id)
    except ProductoNoEncontrado:
        return producto_no_encontrado(request, producto_id)

    # Formulario con los valores ACTUALES del producto.
    # Las cadenas vacías evitan que la plantilla escriba "None".
    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_editar.html",
        context={
            "producto": producto,
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": producto["cantidad"],
            "descripcion": producto["descripcion"] or "",
            "errores": {},
        },
    )


@router.get("/productos/{producto_id}/cancelar")
async def cancelar_edicion_vista(request: Request, conn: ConexionDep, producto_id: int):
    # Cancelar solo vuelve a mostrar la fila original, sin modificar nada.
    try:
        producto = await obtener_producto(conn, producto_id)
    except ProductoNoEncontrado:
        return producto_no_encontrado(request, producto_id)
    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_producto.html",
        context={"producto": producto},
    )


@router.post("/productos/{producto_id}")
async def guardar_producto_vista(
    request: Request,
    conn: ConexionDep,
    producto_id: int,
    nombre: Annotated[str | None, Form()] = None,
    precio: Annotated[str | None, Form()] = None,
    cantidad: Annotated[str | None, Form()] = None,
    descripcion: Annotated[str | None, Form()] = None,
):
    # Los datos llegan como texto desde el formulario. Pydantic se encarga
    # de convertirlos a los tipos correctos (str, float, int) y de validarlos.
    try:
        datos = ProductoActualizar(
            nombre=nombre or "",
            precio=precio,
            cantidad=cantidad,
            descripcion=descripcion or None,
        )
    except ValidationError as exc:
        # Hay errores: NO se toca la base de datos. Se devuelve el formulario
        # con lo que escribió el usuario y los mensajes de error (código 422).
        return templates.TemplateResponse(
            request=request,
            name="componentes/fila_editar.html",
            context={
                "producto": {"id": producto_id},
                "nombre": nombre or "",
                "precio": precio or "",
                "cantidad": cantidad or "",
                "descripcion": descripcion or "",
                "errores": errores_de_validacion(exc),
            },
            status_code=422,
        )

    # Los datos son válidos: el servicio aplica la regla y guarda.
    try:
        await guardar_cambios(
            conn,
            producto_id,
            datos.nombre,
            datos.precio,
            datos.cantidad,
            datos.descripcion,
        )
    except ProductoNoEncontrado:
        return producto_no_encontrado(request, producto_id)

    # Éxito: la fila se reemplaza por los datos nuevos y el aviso verde.
    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_actualizada.html",
        context={
            "producto": {
                "id": producto_id,
                "nombre": datos.nombre,
                "precio": datos.precio,
                "cantidad": datos.cantidad,
                "descripcion": datos.descripcion,
            }
        },
    )


@router.delete("/productos/{producto_id}")
async def eliminar_producto_vista(request: Request, conn: ConexionDep, producto_id: int):
    # HTMX envía esta petición cuando el usuario confirma el borrado
    # (hx-delete + hx-confirm).
    try:
        await borrar_producto(conn, producto_id)
    except ProductoNoEncontrado:
        return producto_no_encontrado(request, producto_id)

    # Éxito: la fila se sustituye por el aviso de que el producto se eliminó.
    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_eliminada.html",
        context={"producto_id": producto_id},
    )
