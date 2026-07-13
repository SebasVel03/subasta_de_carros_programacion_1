"""
Mini panel de manejo de cuentas: se abre al hacer clic en el avatar/nombre
de la barra superior. Pensado para ser rápido — cambiar de cuenta con un
clic — con accesos directos a Configuración y al Perfil completo para lo
que necesite más espacio.
"""

import flet as ft
from theme import Colors
from views.shared import avatar_imagen


def _fila_cuenta_mini(usuario, es_actual, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                avatar_imagen(usuario.foto_perfil, size=32,
                              bgcolor_respaldo=Colors.ACCENT_INDIGO if es_actual else None),
                ft.Column(
                    [
                        ft.Text(usuario.nombre, size=13, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                        ft.Text(usuario.email, size=11, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.Icon(ft.Icons.CHECK, color=Colors.ACCENT_TEAL, size=16) if es_actual else ft.Container(),
            ],
            spacing=10,
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        border_radius=8,
        bgcolor=Colors.SURFACE_ALT if es_actual else None,
        on_click=None if es_actual else (lambda e: on_click(usuario)),
        ink=not es_actual,
    )


def mostrar_panel_cuenta(page: ft.Page, usuario_actual, cuentas_sesion,
                          on_switch_account, on_add_account, on_open_profile,
                          on_open_settings, on_logout) -> None:

    def cerrar():
        page.pop_dialog()
        page.update()

    def wrap(fn):
        def handler(*args):
            cerrar()
            fn(*args)
        return handler

    filas = [_fila_cuenta_mini(u, u.id == usuario_actual.id, wrap(on_switch_account)) for u in cuentas_sesion]

    dialog = ft.AlertDialog(
        modal=False,
        bgcolor=Colors.SURFACE,
        content=ft.Container(
            width=280,
            content=ft.Column(
                [
                    ft.Text("Cuentas", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=6),
                    *filas,
                    ft.Container(height=6),
                    ft.TextButton(
                        content=ft.Row([ft.Icon(ft.Icons.ADD, size=16, color=Colors.ACCENT_INDIGO),
                                         ft.Text("Agregar otra cuenta", color=Colors.ACCENT_INDIGO, size=13)], spacing=6),
                        on_click=lambda e: wrap(on_add_account)(),
                    ),
                    ft.Divider(color=Colors.BORDER, height=1),
                    ft.Container(height=4),
                    ft.TextButton(
                        content=ft.Row([ft.Icon(ft.Icons.PERSON_OUTLINE, size=16, color=Colors.TEXT_PRIMARY),
                                         ft.Text("Ver perfil completo", color=Colors.TEXT_PRIMARY, size=13)], spacing=6),
                        on_click=lambda e: wrap(on_open_profile)(),
                    ),
                    ft.TextButton(
                        content=ft.Row([ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=16, color=Colors.TEXT_PRIMARY),
                                         ft.Text("Configuración", color=Colors.TEXT_PRIMARY, size=13)], spacing=6),
                        on_click=lambda e: wrap(on_open_settings)(),
                    ),
                    ft.TextButton(
                        content=ft.Row([ft.Icon(ft.Icons.LOGOUT, size=16, color="#E26A6A"),
                                         ft.Text("Cerrar sesión", color="#E26A6A", size=13)], spacing=6),
                        on_click=lambda e: wrap(on_logout)(),
                    ),
                ],
                spacing=2,
                tight=True,
            ),
        ),
        actions=[],
    )

    page.show_dialog(dialog)
