"""
Bandeja de mensajes: diálogo con TODAS las conversaciones del usuario activo
en toda la plataforma, sin importar el carro ni si escribió como vendedor o
como comprador. Se abre desde el ícono de mensajes de la barra superior (ver
views/shared.py: top_bar / _boton_mensajes), que además muestra un badge con
el total de mensajes sin leer (backend: contar_mensajes_no_leidos_totales).

A diferencia de la lista de conversaciones dentro del detalle de una
subasta puntual (views/detalle_subasta_dialog.py), que solo el VENDEDOR de
ESE carro puede ver, esta bandeja junta conversaciones de TODOS los carros
en los que el usuario activo participó — sea como vendedor, como postor
interesado, o como comprador coordinando una entrega.

Uso: mostrar_bandeja_mensajes(page, sistema, usuario_actual, on_change)
Esta función arma el diálogo Y lo muestra (page.show_dialog) — el llamador
no necesita hacer nada más.
"""

import flet as ft
from theme import Colors
from views.shared import avatar_imagen, auto_imagen
from views.chat_dialog import mostrar_chat


def _fila_conversacion(conv: dict, on_click) -> ft.Container:
    badge = (
        ft.Container(
            content=ft.Text(str(conv["no_leidos"]), size=11, color=Colors.BACKGROUND, weight=ft.FontWeight.W_600),
            bgcolor=Colors.ACCENT_TEAL, width=20, height=20, border_radius=10,
            alignment=ft.Alignment.CENTER,
        )
        if conv["no_leidos"] else ft.Container(width=20)
    )
    prefijo = "Tú: " if conv["ultimo_mensaje_es_mio"] else ""
    rol_txt = "Vendés" if conv["soy_vendedor_del_carro"] else "Comprás"

    return ft.Container(
        content=ft.Row(
            [
                auto_imagen(conv["carro_imagen"], width=52, height=40, border_radius=6),
                avatar_imagen(conv["otro_usuario_foto"], size=36),
                ft.Column(
                    [
                        ft.Text(
                            f'{conv["otro_usuario_nombre"]} · {conv["carro_marca"]} {conv["carro_modelo"]} '
                            f'({conv["carro_anio"]})',
                            size=13, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(f'{prefijo}{conv["ultimo_mensaje"]}', size=12, color=Colors.TEXT_SECONDARY,
                                 max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Column(
                    [ft.Text(rol_txt, size=10, color=Colors.TEXT_MUTED), badge],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=4,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=10),
        border_radius=8,
        bgcolor=Colors.SURFACE_ALT if conv["no_leidos"] else None,
        on_click=lambda e: on_click(conv),
        ink=True,
    )


def mostrar_bandeja_mensajes(page: ft.Page, sistema, usuario_actual, on_change=None) -> None:
    conversaciones = sistema.obtener_todas_mis_conversaciones(usuario_actual.id)

    def handle_abrir_conversacion(conv: dict):
        # obtener_carro_por_id reconstruye el dict del carro a partir de su
        # id (la conversación solo trae los campos livianos que necesita
        # esta lista, no el dict completo que espera mostrar_chat).
        carro_dict = sistema.obtener_carro_por_id(conv["id_carro"])
        page.pop_dialog()
        page.update()
        if not carro_dict:
            return  # el carro fue borrado/cambiado entre medio; no hay nada que abrir
        mostrar_chat(page, sistema, usuario_actual, carro_dict, conv["otro_usuario_id"], on_change)

    def handle_cerrar(e):
        page.pop_dialog()
        page.update()

    if conversaciones:
        contenido = ft.Column(
            [_fila_conversacion(c, handle_abrir_conversacion) for c in conversaciones],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
            height=420,
        )
    else:
        contenido = ft.Container(
            content=ft.Text("Todavía no tienes conversaciones con nadie.", size=13, color=Colors.TEXT_SECONDARY),
            padding=ft.Padding.symmetric(vertical=24),
            alignment=ft.Alignment.CENTER,
        )

    dialog = ft.AlertDialog(
        modal=False,
        title=ft.Text("Mis Mensajes", size=16, color=Colors.TEXT_PRIMARY),
        bgcolor=Colors.SURFACE,
        content=ft.Container(width=440, content=contenido),
        actions=[
            ft.TextButton(content=ft.Text("Cerrar", color=Colors.TEXT_SECONDARY), on_click=handle_cerrar),
        ],
    )

    page.show_dialog(dialog)
