"""
Pestaña 'MIS CARROS'.

Muestra todo lo que el usuario logueado ha publicado (activo, vendido o
no vendido) y permite publicar un carro nuevo a través de un formulario
plegable que llama a sistema.publicar_carro().
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, estado_badge, empty_state, mensaje_feedback


def _fila_carro(c: dict) -> ft.Container:
    return card(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                 size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                        ft.Text(f'{c["kilometraje"]:,} km · Base {money(c["precio_base"])} · '
                                f'Reserva {money(c["precio_reserva"])}',
                                size=12, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Column(
                    [
                        ft.Text(f'{c["num_pujas"]} pujas · mejor: {money(c["puja_maxima"])}',
                                 size=12, color=Colors.TEXT_SECONDARY),
                        ft.Container(height=4),
                        estado_badge(c["estado_subasta"]),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=0,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=16,
    )


def mis_carros_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None) -> ft.Container:
    mis_carros = sistema.obtener_mis_carros(usuario_actual.id)

    # --- Formulario de publicación (plegable) ---
    estado_form = {"visible": False}

    marca_f = ft.TextField(label="Marca", width=180)
    modelo_f = ft.TextField(label="Modelo", width=180)
    anio_f = ft.TextField(label="Año", width=100)
    km_f = ft.TextField(label="Kilometraje", width=140)
    base_f = ft.TextField(label="Precio base", width=160)
    reserva_f = ft.TextField(label="Precio reserva", width=160)
    dias_f = ft.TextField(label="Días de duración", width=160, value="7")
    error_text = ft.Text("", color="#E26A6A", size=12)

    form_container = ft.Container(visible=False)

    def construir_formulario():
        return card(
            ft.Column(
                [
                    ft.Text("Publicar un carro nuevo", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    ft.Container(height=12),
                    ft.Row([marca_f, modelo_f, anio_f], spacing=12),
                    ft.Container(height=8),
                    ft.Row([km_f, base_f, reserva_f, dias_f], spacing=12),
                    error_text,
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        content=ft.Text("Publicar"),
                        bgcolor=Colors.BUTTON_BG,
                        color=Colors.BUTTON_TEXT,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=handle_publicar,
                    ),
                ],
                spacing=0,
            ),
            padding=20,
        )

    def handle_publicar(e):
        try:
            anio = int(anio_f.value)
            km = int(km_f.value)
            base = float(base_f.value)
            reserva = float(reserva_f.value)
            dias = int(dias_f.value)
        except (TypeError, ValueError):
            error_text.value = "Año, kilometraje, precios y días deben ser números."
            page.update()
            return

        if not marca_f.value or not modelo_f.value:
            error_text.value = "Marca y modelo son obligatorios."
            page.update()
            return

        ok, resultado = sistema.publicar_carro(
            id_vendedor=usuario_actual.id, marca=marca_f.value, modelo=modelo_f.value,
            anio=anio, kilometraje=km, precio_base=base, precio_reserva=reserva,
            dias_duracion=dias,
        )
        if not ok:
            error_text.value = resultado
            page.update()
            return

        if on_change:
            on_change()  # guarda en disco y reconstruye esta misma vista con el carro nuevo

    def toggle_formulario(e):
        estado_form["visible"] = not estado_form["visible"]
        form_container.content = construir_formulario() if estado_form["visible"] else None
        form_container.visible = estado_form["visible"]
        toggle_btn_text.value = "− Cancelar" if estado_form["visible"] else "+ Publicar un carro"
        page.update()

    toggle_btn_text = ft.Text("+ Publicar un carro")
    toggle_btn = ft.ElevatedButton(
        content=toggle_btn_text,
        bgcolor=Colors.BUTTON_BG,
        color=Colors.BUTTON_TEXT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=toggle_formulario,
    )

    lista = [_fila_carro(c) for c in mis_carros] if mis_carros else [
        empty_state("Todavía no has publicado ningún carro.")
    ]

    body = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Mis Carros", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    toggle_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=Sizes.GAP),
            form_container,
            ft.Container(height=Sizes.GAP if estado_form["visible"] else 0),
            *[item for c in lista for item in (c, ft.Container(height=12))],
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "MIS CARROS", body, on_nav_click=on_nav_click)
