"""
Pestaña 'VENTAS'.

Historial de subastas YA CERRADAS de este usuario como vendedor: vendidas
(con comprador y comisión de plataforma) y no vendidas (no alcanzaron la
reserva o no tuvieron pujas).
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, estado_badge, empty_state, auto_imagen


def _fila_venta(c: dict) -> ft.Container:
    if c["estado_subasta"] == "vendido":
        detalle = f'Vendido a {c["comprador_nombre"]} por {money(c["precio_final_venta"])} · ' \
                   f'Comisión plataforma: {money(c["comision"])}'
    else:
        detalle = "No se vendió (sin pujas o no se alcanzó el precio de reserva)."

    return card(
        ft.Row(
            [
                auto_imagen(c.get("imagen"), width=90, height=68),
                ft.Column(
                    [
                        ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                 size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                        ft.Text(detalle, size=12, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=2,
                    expand=True,
                ),
                estado_badge(c["estado_subasta"]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=16,
        ),
        padding=16,
    )


def ventas_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None, on_profile_click=None) -> ft.Container:
    ventas = sistema.obtener_mis_ventas(usuario_actual.id)

    vendidos = [v for v in ventas if v["estado_subasta"] == "vendido"]
    total_vendido = sum(v["precio_final_venta"] for v in vendidos)
    total_comision = sum(v["comision"] for v in vendidos)

    resumen_row = ft.Row(
        [
            card(
                ft.Column([
                    ft.Text("AUTOS VENDIDOS", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(str(len(vendidos)), size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                expand=True,
            ),
            card(
                ft.Column([
                    ft.Text("TOTAL VENDIDO", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(money(total_vendido), size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                expand=True,
            ),
            card(
                ft.Column([
                    ft.Text("COMISIÓN PAGADA", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(money(total_comision), size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                expand=True,
            ),
        ],
        spacing=Sizes.GAP,
    )

    lista = [_fila_venta(c) for c in ventas] if ventas else [
        empty_state("Todavía no tienes subastas cerradas como vendedor.")
    ]

    body = ft.Column(
        [
            ft.Text("Ventas", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text("Historial de tus subastas ya cerradas.", size=13, color=Colors.TEXT_SECONDARY),
            ft.Container(height=Sizes.GAP),
            resumen_row,
            ft.Container(height=Sizes.GAP),
            *[item for c in lista for item in (c, ft.Container(height=12))],
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "VENTAS", body, on_nav_click=on_nav_click, on_profile_click=on_profile_click)
