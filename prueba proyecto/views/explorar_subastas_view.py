"""
Pestaña 'EXPLORAR SUBASTAS'.

Muestra TODAS las subastas activas de la plataforma (no solo las del usuario)
y permite pujar directamente desde la lista, llamando a sistema.registrar_puja().
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, empty_state


def _fila_subasta(c: dict, sistema, usuario_actual, page, on_change) -> ft.Container:
    monto_field = ft.TextField(
        hint_text=f'> {money(c["puja_maxima"])}',
        width=140,
        height=42,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        text_size=13,
    )
    feedback = ft.Text("", size=12)

    def handle_pujar(e):
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
            on_change()  # guarda y reconstruye la vista con la nueva puja_maxima

    horas = c["horas_restantes"]
    tiempo_txt = f'{horas:.0f} h restantes' if horas is not None and horas < 48 else (
        f'{horas / 24:.0f} d restantes' if horas is not None else 'sin fecha de cierre'
    )

    pujar_btn = ft.ElevatedButton(
        content=ft.Text("Pujar", size=13),
        bgcolor=Colors.BUTTON_BG,
        color=Colors.BUTTON_TEXT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=handle_pujar,
        disabled=c["es_propio"],
    )

    controles_derecha = (
        [ft.Text("Es tu propio carro", size=12, color=Colors.TEXT_SECONDARY)]
        if c["es_propio"] else
        [monto_field, pujar_btn]
    )

    return card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                         size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                                ft.Text(f'{c["kilometraje"]:,} km · {c["num_pujas"]} pujas · {tiempo_txt}',
                                         size=12, color=Colors.TEXT_SECONDARY),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Column(
                            [
                                ft.Text("Puja más alta", size=11, color=Colors.TEXT_SECONDARY),
                                ft.Text(money(c["puja_maxima"]), size=16, weight=ft.FontWeight.BOLD,
                                         color=Colors.TEXT_PRIMARY),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=10),
                ft.Row(controles_derecha, alignment=ft.MainAxisAlignment.END, spacing=10),
                feedback,
            ],
            spacing=0,
        ),
        padding=16,
    )


def explorar_subastas_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None) -> ft.Container:
    subastas = sistema.obtener_subastas_explorar(id_usuario=usuario_actual.id)

    if subastas:
        filas = [_fila_subasta(c, sistema, usuario_actual, page, on_change) for c in subastas]
        lista = [item for c in filas for item in (c, ft.Container(height=12))]
    else:
        lista = [empty_state("No hay subastas activas en la plataforma por ahora.")]

    body = ft.Column(
        [
            ft.Text("Explorar Subastas", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text("Todas las subastas activas del mercado.", size=13, color=Colors.TEXT_SECONDARY),
            ft.Container(height=Sizes.GAP),
            *lista,
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "EXPLORAR SUBASTAS", body, on_nav_click=on_nav_click)
