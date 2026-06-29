"""
Pestaña 'SUBASTAS ACTIVAS'.

A diferencia de 'EXPLORAR SUBASTAS' (todo el mercado), esta pestaña muestra
solo las subastas activas en las que el usuario YA participa: tiene una
oferta registrada o la marcó como favorita. También deja subir la puja.
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, empty_state, auto_imagen

ESTADO_OFERTA_COLOR = {
    "Activa": "#7ED957",
    "Superada": "#E2B33E",
    "Ganada": "#7ED957",
    "Perdida": "#E26A6A",
    "Solo en favoritos": Colors.TEXT_SECONDARY,
}


def _fila_mi_subasta(c: dict, sistema, usuario_actual, page, on_change) -> ft.Container:
    monto_field = ft.TextField(
        hint_text=f'> {money(c["puja_maxima"])}',
        width=140,
        height=42,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        text_size=13,
    )
    feedback = ft.Text("", size=12)

    def handle_subir_puja(e):
        try:
            monto = float(monto_field.value)
        except (TypeError, ValueError):
            feedback.value = "Ingresa un monto válido."
            feedback.color = "#E26A6A"
            page.update()
            return

        ok, resultado = sistema.registrar_puja(usuario_actual.id, c["id"], monto)
        if not ok:
            feedback.value = resultado
            feedback.color = "#E26A6A"
            page.update()
            return

        if on_change:
            on_change()

    color_estado = ESTADO_OFERTA_COLOR.get(c["mi_estado"], Colors.TEXT_SECONDARY)
    mi_monto_txt = money(c["mi_monto"]) if c["mi_monto"] is not None else "—"

    return card(
        ft.Column(
            [
                ft.Row(
                    [
                        auto_imagen(c.get("imagen"), width=90, height=68),
                        ft.Column(
                            [
                                ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                         size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                                ft.Text(f'Tu oferta: {mi_monto_txt}  ·  Puja más alta: {money(c["puja_maxima"])}',
                                         size=12, color=Colors.TEXT_SECONDARY),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text(c["mi_estado"], size=11, weight=ft.FontWeight.W_600, color=Colors.BACKGROUND),
                            bgcolor=color_estado,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                            border_radius=6,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=16,
                ),
                ft.Container(height=10),
                ft.Row([monto_field,
                        ft.ElevatedButton(
                            content=ft.Text("Subir puja", size=13),
                            bgcolor=Colors.BUTTON_BG,
                            color=Colors.BUTTON_TEXT,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=handle_subir_puja,
                        )],
                       alignment=ft.MainAxisAlignment.END, spacing=10),
                feedback,
            ],
            spacing=0,
        ),
        padding=16,
    )


def subastas_activas_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None, on_profile_click=None) -> ft.Container:
    mis_subastas = sistema.obtener_mis_subastas_activas(usuario_actual.id)

    if mis_subastas:
        filas = [_fila_mi_subasta(c, sistema, usuario_actual, page, on_change) for c in mis_subastas]
        lista = [item for c in filas for item in (c, ft.Container(height=12))]
    else:
        lista = [empty_state(
            "Todavía no tienes pujas ni favoritos en subastas activas.\n"
            "Ve a 'Explorar Subastas' para empezar a participar."
        )]

    body = ft.Column(
        [
            ft.Text("Subastas Activas", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text("Las subastas en las que ya estás participando.", size=13, color=Colors.TEXT_SECONDARY),
            ft.Container(height=Sizes.GAP),
            *lista,
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "SUBASTAS ACTIVAS", body, on_nav_click=on_nav_click, on_profile_click=on_profile_click)
