"""
Pestaña 'EXPLORAR SUBASTAS'.

Muestra las subastas activas de la plataforma (no solo las del usuario).
Cada tarjeta es clickeable y abre el panel de detalle con la imagen ampliada
y toda la info del carro (ver views/detalle_subasta_dialog.py); pujar
también se puede hacer directo desde la tarjeta, sin abrir el detalle.
El cuadro de búsqueda de la barra superior filtra por marca/modelo/año.
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, empty_state, auto_imagen
from views.detalle_subasta_dialog import mostrar_detalle_subasta


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

    def handle_abrir_detalle(e):
        mostrar_detalle_subasta(page, sistema, usuario_actual, c, on_change)

    horas = c["horas_restantes"]
    # Mismo criterio que _tiempo_restante_texto() en detalle_subasta_dialog.py:
    # sin este chequeo, una subasta que venció a mitad de sesión (ver
    # sistema.cerrar_subastas_vencidas, que solo corre al iniciar la app)
    # mostraba algo confuso como "-3 h restantes" en vez de "Cerrada".
    if horas is None:
        tiempo_txt = "sin fecha de cierre"
    elif horas <= 0:
        tiempo_txt = "cerrada"
    elif horas < 48:
        tiempo_txt = f"{horas:.0f} h restantes"
    else:
        tiempo_txt = f"{horas / 24:.0f} d restantes"

    pujar_btn = ft.ElevatedButton(
        content=ft.Text("Pujar", size=13),
        bgcolor=Colors.BUTTON_BG,
        color=Colors.BUTTON_TEXT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=handle_pujar,
        disabled=c["es_propio"],
    )

    controles_derecha: list[ft.Control] = (
        [ft.Text("Es tu propio carro", size=12, color=Colors.TEXT_SECONDARY)]
        if c["es_propio"] else
        [monto_field, pujar_btn]
    )

    # La imagen y el texto abren el detalle; los controles de puja (dentro
    # de su propia fila) no, para que hacer clic en el campo de monto no
    # dispare accidentalmente la apertura del panel completo.
    contenido: list[ft.Control] = [
        ft.Row(
            [
                ft.Container(
                    content=auto_imagen(c.get("imagen"), width=90, height=68),
                    on_click=handle_abrir_detalle,
                    ink=True,
                    border_radius=8,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                     size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                            ft.Text(f'{c["kilometraje"]:,} km · {c["num_pujas"]} pujas · {tiempo_txt}',
                                     size=12, color=Colors.TEXT_SECONDARY),
                        ],
                        spacing=2,
                    ),
                    on_click=handle_abrir_detalle,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Puja más alta", size=11, color=Colors.TEXT_SECONDARY),
                            ft.Text(money(c["puja_maxima"]), size=16, weight=ft.FontWeight.BOLD,
                                     color=Colors.TEXT_PRIMARY),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=0,
                    ),
                    on_click=handle_abrir_detalle,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=16,
        ),
        ft.Container(height=10),
        ft.Row(controles_derecha, alignment=ft.MainAxisAlignment.END, spacing=10),
        feedback,
    ]

    return card(
        ft.Column(contenido, spacing=0),
        padding=16,
    )


def explorar_subastas_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None,
                            on_account_click=None, on_search=None, valor_busqueda="",
                            on_messages_click=None) -> ft.Container:
    subastas = sistema.obtener_subastas_explorar(id_usuario=usuario_actual.id, filtro_texto=valor_busqueda or None)

    if subastas:
        filas = [_fila_subasta(c, sistema, usuario_actual, page, on_change) for c in subastas]
        lista = [item for c in filas for item in (c, ft.Container(height=12))]
    elif valor_busqueda:
        lista = [empty_state(f'No hay subastas activas que coincidan con "{valor_busqueda}".')]
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

    return page_shell(usuario_actual, "EXPLORAR SUBASTAS", body, sistema=sistema, on_nav_click=on_nav_click,
                       on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda,
                       on_messages_click=on_messages_click)
