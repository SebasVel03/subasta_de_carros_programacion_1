"""
Pantalla de Perfil (se abre al hacer clic en el nombre/avatar de la barra
superior, no es una pestaña más del menú). Incluye:

- Información básica de la cuenta activa.
- Configuración simple: editar nombre/teléfono, cambiar contraseña.
- Selector de cuentas: si la persona inició sesión con más de una cuenta en
  esta misma sesión de la app, puede cambiar entre ellas sin volver a
  escribir la contraseña, agregar otra cuenta, o cerrar sesión.
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, empty_state


def _fila_cuenta(usuario, es_actual, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.PERSON, color=Colors.TEXT_PRIMARY, size=18),
                    bgcolor=Colors.ACCENT_INDIGO if es_actual else Colors.SURFACE_ALT,
                    radius=18,
                ),
                ft.Column(
                    [
                        ft.Text(usuario.nombre, size=13, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                        ft.Text(usuario.email, size=11, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=Colors.ACCENT_TEAL, size=18) if es_actual else ft.Container(),
            ],
            spacing=10,
        ),
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        border_radius=8,
        bgcolor=Colors.SURFACE_ALT if es_actual else None,
        on_click=None if es_actual else (lambda e: on_click(usuario)),
    )


def perfil_view(page: ft.Page, sistema, usuario_actual, cuentas_sesion=None,
                 on_nav_click=None, on_change=None, on_account_click=None, on_search=None, valor_busqueda="",
                 on_switch_account=None, on_add_account=None, on_logout=None) -> ft.Container:
    cuentas_sesion = cuentas_sesion or ([usuario_actual] if usuario_actual else [])

    # --- Tarjeta de información básica ---
    info_card = card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color=Colors.TEXT_PRIMARY, size=28),
                            bgcolor=Colors.SURFACE_ALT,
                            radius=32,
                        ),
                        ft.Column(
                            [
                                ft.Text(usuario_actual.nombre, size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                ft.Text(usuario_actual.email, size=13, color=Colors.TEXT_SECONDARY),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=16,
                ),
                ft.Container(height=16),
                ft.Divider(color=Colors.BORDER, height=1),
                ft.Container(height=16),
                ft.Row(
                    [
                        ft.Column([ft.Text("ROL", size=11, color=Colors.TEXT_SECONDARY),
                                    ft.Text(usuario_actual.rol.capitalize(), size=14, color=Colors.TEXT_PRIMARY)], spacing=2),
                        ft.Column([ft.Text("VERIFICADO", size=11, color=Colors.TEXT_SECONDARY),
                                    ft.Text("Sí" if usuario_actual.verificado else "No", size=14, color=Colors.TEXT_PRIMARY)], spacing=2),
                        ft.Column([ft.Text("REPUTACIÓN", size=11, color=Colors.TEXT_SECONDARY),
                                    ft.Text(f"{usuario_actual.reputacion} ⭐", size=14, color=Colors.TEXT_PRIMARY)], spacing=2),
                        ft.Column([ft.Text("MIEMBRO DESDE", size=11, color=Colors.TEXT_SECONDARY),
                                    ft.Text((usuario_actual.fecha_registro or "")[:10], size=14, color=Colors.TEXT_PRIMARY)], spacing=2),
                    ],
                    spacing=28,
                ),
            ],
            spacing=0,
        ),
        padding=20,
    )

    # --- Configuración: editar datos básicos ---
    nombre_f = ft.TextField(label="Nombre completo", value=usuario_actual.nombre, width=300)
    telefono_f = ft.TextField(label="Teléfono", value=usuario_actual.telefono or "", width=300)
    datos_feedback = ft.Text("", size=12)

    def handle_guardar_datos(e):
        ok, resultado = sistema.actualizar_perfil(usuario_actual.id, nombre=nombre_f.value, telefono=telefono_f.value)
        if not ok:
            datos_feedback.value = resultado
            datos_feedback.color = "#E26A6A"
            page.update()
            return
        datos_feedback.value = "Datos actualizados."
        datos_feedback.color = Colors.ACCENT_TEAL
        if on_change:
            on_change()
        else:
            page.update()

    datos_card = card(
        ft.Column(
            [
                ft.Text("Información básica", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Container(height=12),
                ft.Row([nombre_f, telefono_f], spacing=12),
                datos_feedback,
                ft.Container(height=8),
                ft.ElevatedButton(
                    content=ft.Text("Guardar cambios"),
                    bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=handle_guardar_datos,
                ),
            ],
            spacing=0,
        ),
        padding=20,
        expand=True,
    )

    # --- Configuración: cambiar contraseña ---
    actual_f = ft.TextField(label="Contraseña actual", password=True, can_reveal_password=True, width=300)
    nueva_f = ft.TextField(label="Contraseña nueva", password=True, can_reveal_password=True, width=300)
    password_feedback = ft.Text("", size=12)

    def handle_cambiar_password(e):
        ok, resultado = sistema.cambiar_password(usuario_actual.id, actual_f.value or "", nueva_f.value or "")
        if not ok:
            password_feedback.value = resultado
            password_feedback.color = "#E26A6A"
            page.update()
            return
        actual_f.value = ""
        nueva_f.value = ""
        password_feedback.value = "Contraseña actualizada."
        password_feedback.color = Colors.ACCENT_TEAL
        if on_change:
            on_change()
        else:
            page.update()

    password_card = card(
        ft.Column(
            [
                ft.Text("Cambiar contraseña", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Container(height=12),
                ft.Row([actual_f, nueva_f], spacing=12),
                password_feedback,
                ft.Container(height=8),
                ft.ElevatedButton(
                    content=ft.Text("Actualizar contraseña"),
                    bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=handle_cambiar_password,
                ),
            ],
            spacing=0,
        ),
        padding=20,
        expand=True,
    )

    # --- Selector de cuentas ---
    filas_cuentas = [
        _fila_cuenta(u, u.id == usuario_actual.id, on_switch_account)
        for u in cuentas_sesion
    ]

    cuentas_card = card(
        ft.Column(
            [
                ft.Text("Cuentas en esta sesión", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Text("Cambia entre cuentas sin volver a escribir la contraseña.",
                         size=11, color=Colors.TEXT_MUTED),
                ft.Container(height=12),
                *filas_cuentas,
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.TextButton(
                            content=ft.Text("+ Agregar otra cuenta", color=Colors.ACCENT_INDIGO, size=13),
                            on_click=(lambda e: on_add_account()) if on_add_account else None,
                        ),
                        ft.TextButton(
                            content=ft.Text("Cerrar sesión", color="#E26A6A", size=13),
                            on_click=(lambda e: on_logout()) if on_logout else None,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=4,
        ),
        padding=20,
    )

    body = ft.Column(
        [
            ft.Text("Perfil", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Container(height=Sizes.GAP),
            info_card,
            ft.Container(height=Sizes.GAP),
            ft.Row([datos_card, password_card], spacing=Sizes.GAP, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Container(height=Sizes.GAP),
            cuentas_card,
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "PERFIL", body, on_nav_click=on_nav_click, on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda)
