"""
Componentes de UI compartidos entre las 5 pantallas (RESUMEN, MIS CARROS,
EXPLORAR SUBASTAS, SUBASTAS ACTIVAS, VENTAS), para no repetir la barra
superior ni los helpers de formato en cada archivo de vista.
"""

import flet as ft
from theme import Colors, Sizes, card

NAV_TABS = ["RESUMEN", "MIS CARROS", "EXPLORAR SUBASTAS", "SUBASTAS ACTIVAS", "VENTAS"]

ESTADO_COLORES = {
    "activa": Colors.ACCENT_TEAL,
    "vendido": "#7ED957",
    "no_vendido": "#E26A6A",
}


def money(valor: float) -> str:
    return f"${valor:,.2f}"


def top_bar(usuario_actual, active_tab: str, on_nav_click=None) -> ft.Container:
    tabs = []
    for label in NAV_TABS:
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
            ft.Row(
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
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    nav_row = ft.Row(
        [
            ft.Row(tabs, spacing=4),
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


def page_shell(usuario_actual, active_tab, body, on_nav_click=None) -> ft.Container:
    """Envuelve cualquier 'body' con la barra superior + scroll + fondo, igual en las 5 pantallas."""
    return ft.Container(
        content=ft.Column(
            [
                top_bar(usuario_actual, active_tab, on_nav_click=on_nav_click),
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
