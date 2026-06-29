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


def money(valor: float) -> str:
    return f"${valor:,.2f}"


def tabs_para_usuario(usuario_actual) -> list:
    """Los admins/expertos ven una pestaña extra para revisar publicaciones."""
    tabs = list(BASE_TABS)
    if usuario_actual and usuario_actual.rol == "admin":
        tabs.append("REVISIÓN")
    return tabs


def auto_imagen(imagen, width=96, height=72, border_radius=8) -> ft.Control:
    """
    Muestra la foto del vehículo si existe (acepta URL o string base64,
    Flet detecta cuál es), o un placeholder si todavía no se cargó ninguna.
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
        content=ft.Icon(ft.Icons.DIRECTIONS_CAR, color=Colors.TEXT_MUTED, size=28),
        width=width,
        height=height,
        bgcolor=Colors.SURFACE_ALT,
        border_radius=border_radius,
        alignment=ft.Alignment.CENTER,
    )


def top_bar(usuario_actual, active_tab: str, on_nav_click=None, on_profile_click=None) -> ft.Container:
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

    header_row = ft.Row(
        [
            ft.Text("APP SUBASTAS", size=16, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.MORE_HORIZ, color=Colors.NAV_PILL_TEXT, size=18),
                            bgcolor=Colors.NAV_PILL_BG,
                            width=40,
                            height=40,
                            border_radius=20,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Text(usuario_actual.nombre if usuario_actual else "", size=13, color=Colors.TEXT_SECONDARY),
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color=Colors.TEXT_PRIMARY),
                            bgcolor=Colors.SURFACE_ALT,
                            radius=18,
                        ),
                        ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, color=Colors.TEXT_SECONDARY, size=18),
                    ],
                    spacing=10,
                ),
                on_click=(lambda e: on_profile_click()) if on_profile_click else None,
                border_radius=24,
                padding=ft.Padding.symmetric(horizontal=4, vertical=4),
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    nav_row = ft.Row(
        [
            ft.Row(tabs, spacing=4, run_spacing=8, wrap=True),
            ft.Container(
                content=ft.TextField(
                    hint_text="Buscar...",
                    hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
                    prefix_icon=ft.Icons.SEARCH,
                    bgcolor=Colors.SURFACE,
                    border_color=Colors.BORDER,
                    border_radius=8,
                    color=Colors.TEXT_PRIMARY,
                    height=42,
                    content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    text_size=13,
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


def page_shell(usuario_actual, active_tab, body, on_nav_click=None, on_profile_click=None) -> ft.Container:
    """Envuelve cualquier 'body' con la barra superior + scroll + fondo, igual en todas las pantallas."""
    return ft.Container(
        content=ft.Column(
            [
                top_bar(usuario_actual, active_tab, on_nav_click=on_nav_click, on_profile_click=on_profile_click),
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
                         color=Colors.BACKGROUND),
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
