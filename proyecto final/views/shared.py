"""
Componentes de UI compartidos entre las pantallas (RESUMEN, MIS CARROS,
EXPLORAR SUBASTAS, SUBASTAS ACTIVAS, VENTAS, REVISIÓN), para no repetir la
barra superior ni los helpers de formato en cada archivo de vista.
"""

import flet as ft
from theme import Colors, Sizes, card

BASE_TABS = ["RESUMEN", "MIS CARROS", "EXPLORAR SUBASTAS", "SUBASTAS ACTIVAS", "VENTAS"]

ESTADO_COLORES = {
    "pendiente_revision": "#E2B33E",
    "activa": Colors.ACCENT_TEAL,
    "vendido": "#7ED957",
    "no_vendido": "#E26A6A",
    "rechazada": "#8A8AA3",
}

# Límite para cualquier imagen subida desde el dispositivo (fotos de carros
# en Mis Carros y foto de perfil en Perfil comparten este límite y la misma
# lógica de codificación a base64 — un archivo elegido con ft.FilePicker se
# lee en bytes y se guarda como string base64 en el .json correspondiente).
TAMANO_MAXIMO_IMAGEN_MB = 5
TAMANO_MAXIMO_IMAGEN_BYTES = TAMANO_MAXIMO_IMAGEN_MB * 1024 * 1024


def money(valor: float) -> str:
    return f"${valor:,.2f}"


def tabs_para_usuario(usuario_actual) -> list:
    """Los admins/expertos ven una pestaña extra para revisar publicaciones."""
    tabs = list(BASE_TABS)
    if usuario_actual and usuario_actual.rol == "admin":
        tabs.append("REVISIÓN")
    return tabs


def auto_imagen(imagen, width=96, height=72, border_radius=8, icono=ft.Icons.DIRECTIONS_CAR) -> ft.Control:
    """
    Muestra una imagen si existe (acepta URL o string base64, Flet detecta
    cuál es), o un ícono de respaldo si todavía no se cargó ninguna o si
    falla la carga. Un solo helper para dos casos de uso en el proyecto:
    fotos de carros (ícono de auto, el valor por defecto) y fotos de perfil
    de usuario (ícono de persona — ver avatar_imagen más abajo, que es un
    envoltorio circular de esta misma función). Solo cambian
    width/height/border_radius/icono entre un caso y otro.
    """
    if imagen:
        return ft.Image(
            src=imagen,
            width=width,
            height=height,
            fit=ft.BoxFit.COVER,
            border_radius=border_radius,
            error_content=ft.Container(
                content=ft.Icon(ft.Icons.BROKEN_IMAGE, color=Colors.TEXT_MUTED),
                width=width, height=height, bgcolor=Colors.SURFACE_ALT,
                border_radius=border_radius, alignment=ft.Alignment.CENTER,
            ),
        )
    return ft.Container(
        content=ft.Icon(icono, color=Colors.TEXT_MUTED, size=min(28, width // 3)),
        width=width,
        height=height,
        bgcolor=Colors.SURFACE_ALT,
        border_radius=border_radius,
        alignment=ft.Alignment.CENTER,
    )


def avatar_imagen(foto_perfil, size=36, bgcolor_respaldo=None) -> ft.Control:
    """
    Versión circular de auto_imagen(), pensada para la foto de perfil de un
    usuario (en vez de la foto de un carro): mismo mecanismo — acepta URL o
    string base64, con un ícono de persona como respaldo si no hay foto o si
    falla la carga —, recortada en círculo (border_radius = mitad del
    tamaño).

    bgcolor_respaldo: opcional, para casos donde el círculo de respaldo (sin
    foto) necesita un color propio en vez del gris por defecto — por ejemplo
    para resaltar la cuenta activa en el selector de cuentas. No tiene efecto
    si el usuario sí tiene una foto puesta.
    """
    radio = size / 2
    control = auto_imagen(foto_perfil, width=size, height=size, border_radius=radio, icono=ft.Icons.PERSON)
    if not foto_perfil and bgcolor_respaldo:
        control.bgcolor = bgcolor_respaldo
    return control


def boton_icono_con_badge(icono, count: int, on_click=None, tooltip=None) -> ft.Container:
    """
    Ícono circular con un badge numérico (ft.Badge nativo de Flet) cuando
    count > 0. Extraído de lo que antes era solo _boton_mensajes, para que
    lo pueda reusar cualquier otro ícono con la misma pinta -- hoy además lo
    usa el ícono de notificaciones de 'Subastas Activas' (ver
    views/subastas_activas_view.py / views/notificaciones_dialog.py).
    """
    badge = None
    if count:
        etiqueta = str(count) if count <= 9 else "9+"
        badge = ft.Badge(label=etiqueta, bgcolor=Colors.ACCENT_TEAL, text_color=Colors.TEXT_ON_ACCENT)
    return ft.Container(
        content=ft.Icon(icono, color=Colors.TEXT_PRIMARY, size=22),
        badge=badge,
        width=36,
        height=36,
        border_radius=18,
        alignment=ft.Alignment.CENTER,
        on_click=(lambda e: on_click()) if on_click else None,
        ink=on_click is not None,
        tooltip=tooltip,
    )


def _boton_mensajes(mensajes_no_leidos: int, on_messages_click=None) -> ft.Container:
    """
    Ícono de la bandeja de mensajes para la barra superior, con un badge de
    conteo cuando hay mensajes sin leer. Al hacer clic abre
    views/bandeja_mensajes_dialog.py con TODAS las conversaciones del
    usuario activo en toda la plataforma — a diferencia de la lista de
    conversaciones dentro del detalle de una subasta puntual
    (views/detalle_subasta_dialog.py), que solo puede ver el VENDEDOR de ESE
    carro.

    mensajes_no_leidos se calcula en page_shell() (a partir de
    sistema.contar_mensajes_no_leidos_totales) cada vez que se reconstruye
    la pantalla, así que el badge queda al día después de cualquier acción,
    de cambiar de pestaña, o de volver a abrir la bandeja. No hay un
    mecanismo de aviso en tiempo real mientras la persona está quieta en una
    pantalla (la app no tiene sockets/push); si dos personas usan
    instancias separadas de la app contra los mismos .json, el badge de una
    instancia no se entera de un mensaje nuevo de la otra hasta el próximo
    re-render de esa instancia.
    """
    return boton_icono_con_badge(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, mensajes_no_leidos, on_messages_click)


def top_bar(usuario_actual, active_tab: str, on_nav_click=None, on_account_click=None,
            on_search=None, valor_busqueda="", on_messages_click=None, mensajes_no_leidos=0) -> ft.Container:
    tabs = []
    for label in tabs_para_usuario(usuario_actual):
        is_active = label == active_tab
        tabs.append(
            ft.Container(
                content=ft.Text(
                    label,
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=Colors.NAV_PILL_TEXT if is_active else Colors.TEXT_SECONDARY,
                ),
                bgcolor=Colors.NAV_PILL_BG if is_active else None,
                padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                border_radius=8,
                on_click=(lambda e, l=label: on_nav_click(l)) if on_nav_click else None,
            )
        )

    def handle_buscar_submit(e):
        if on_search:
            on_search((e.control.value or "").strip())

    header_row = ft.Row(
        [
            ft.Text("APP SUBASTAS", size=16, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            # Mensajes + cuenta: el ícono de mensajes abre la bandeja global
            # (ver _boton_mensajes arriba); la cuenta (avatar + nombre +
            # flecha) abre el mini panel de manejo de cuentas, no navega
            # directo a ningún lado por sí misma.
            ft.Row(
                [
                    _boton_mensajes(mensajes_no_leidos, on_messages_click),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(usuario_actual.nombre if usuario_actual else "", size=13, color=Colors.TEXT_SECONDARY),
                                avatar_imagen(usuario_actual.foto_perfil if usuario_actual else None, size=36),
                                ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, color=Colors.TEXT_SECONDARY, size=18),
                            ],
                            spacing=10,
                        ),
                        on_click=(lambda e: on_account_click()) if on_account_click else None,
                        border_radius=24,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    ),
                ],
                spacing=4,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    nav_row = ft.Row(
        [
            ft.Row(tabs, spacing=4, run_spacing=8, wrap=True),
            ft.Container(
                content=ft.TextField(
                    hint_text="Buscar subastas (marca, modelo, año)...",
                    hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
                    prefix_icon=ft.Icons.SEARCH,
                    bgcolor=Colors.SURFACE,
                    border_color=Colors.BORDER,
                    border_radius=8,
                    color=Colors.TEXT_PRIMARY,
                    height=42,
                    content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    text_size=13,
                    value=valor_busqueda,
                    on_submit=handle_buscar_submit,
                ),
                width=300,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    return ft.Container(
        content=ft.Column([header_row, ft.Container(height=18), nav_row], spacing=0),
        padding=ft.Padding.symmetric(horizontal=Sizes.PAGE_PADDING, vertical=20),
    )


def page_shell(usuario_actual, active_tab, body, sistema=None, on_nav_click=None, on_account_click=None,
               on_search=None, valor_busqueda="", on_messages_click=None) -> ft.Container:
    """Envuelve cualquier 'body' con la barra superior + scroll + fondo, igual en todas las pantallas.

    sistema: opcional. Se usa únicamente para calcular cuántos mensajes sin
    leer tiene la cuenta activa (ver contar_mensajes_no_leidos_totales en
    backend/sistema.py) y mostrar el badge en el ícono de mensajes de la
    barra superior. Si no se pasa (o no hay usuario activo todavía), el
    ícono simplemente se muestra sin badge.
    """
    mensajes_no_leidos = (
        sistema.contar_mensajes_no_leidos_totales(usuario_actual.id)
        if (sistema and usuario_actual) else 0
    )
    return ft.Container(
        content=ft.Column(
            [
                top_bar(usuario_actual, active_tab, on_nav_click=on_nav_click,
                        on_account_click=on_account_click, on_search=on_search,
                        valor_busqueda=valor_busqueda, on_messages_click=on_messages_click,
                        mensajes_no_leidos=mensajes_no_leidos),
                ft.Container(
                    content=body,
                    padding=ft.Padding.symmetric(horizontal=Sizes.PAGE_PADDING, vertical=10),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor=Colors.BACKGROUND,
        expand=True,
    )


def estado_badge(estado_subasta: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(estado_subasta.replace("_", " ").upper(), size=11, weight=ft.FontWeight.W_600,
                         color=Colors.TEXT_ON_ACCENT),
        bgcolor=ESTADO_COLORES.get(estado_subasta, Colors.TEXT_SECONDARY),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=6,
    )


def empty_state(mensaje: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(mensaje, size=13, color=Colors.TEXT_SECONDARY),
        padding=ft.Padding.symmetric(vertical=24),
        alignment=ft.Alignment.CENTER,
    )


def mensaje_feedback(texto: str, es_error: bool) -> ft.Text:
    return ft.Text(texto, size=12, color="#E26A6A" if es_error else Colors.ACCENT_TEAL)
