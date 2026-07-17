"""
Panel de notificaciones: diálogo con los avisos del sistema para el usuario
activo (por ahora, solo "te superaron una puja" — ver
sistema.crear_notificacion / registrar_puja en backend/sistema.py). Se abre
desde el ícono de campana en 'Subastas Activas' (ver
views/subastas_activas_view.py), que muestra un badge con el total de
notificaciones sin leer (sistema.contar_notificaciones_no_leidas) — mismo
mecanismo que el ícono de mensajes de la barra superior (ver
views/shared.py: boton_icono_con_badge).

A diferencia del aviso emergente (SnackBar) que aparece una sola vez apenas
se genera la notificación (ver main.py: avisar_notificaciones_nuevas), este
panel junta el HISTORIAL completo, se puede volver a abrir cuando sea, y
abrirlo es lo que marca las notificaciones como leídas (bajando el badge) —
mismo criterio que abrir un chat marca sus mensajes como leídos.

Uso: mostrar_notificaciones(page, sistema, usuario_actual, on_change)
Esta función arma el diálogo Y lo muestra (page.show_dialog) — el llamador
no necesita hacer nada más.
"""

import flet as ft
from theme import Colors


def _fila_notificacion(n: dict) -> ft.Container:
    fecha = (n["fecha_hora"] or "")[:16].replace("T", " ")
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(n["texto"], size=13, color=Colors.TEXT_PRIMARY),
                ft.Text(fecha, size=11, color=Colors.TEXT_MUTED),
            ],
            spacing=2,
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=10),
        border_radius=8,
        bgcolor=Colors.SURFACE_ALT if not n["leido"] else None,
    )


def mostrar_notificaciones(page: ft.Page, sistema, usuario_actual, on_change=None) -> None:
    notificaciones = sistema.obtener_notificaciones_usuario(usuario_actual.id)

    # Abrir el panel marca todo como leído -- se persiste de inmediato junto
    # con el resto del estado, igual que al abrir un chat.
    sistema.marcar_notificaciones_leidas(usuario_actual.id)
    if on_change:
        on_change()

    def handle_cerrar(e):
        page.pop_dialog()
        page.update()

    if notificaciones:
        contenido = ft.Column(
            [_fila_notificacion(n) for n in notificaciones],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
            height=380,
        )
    else:
        contenido = ft.Container(
            content=ft.Text("Todavía no tenés notificaciones.", size=13, color=Colors.TEXT_SECONDARY),
            padding=ft.Padding.symmetric(vertical=24),
            alignment=ft.Alignment.CENTER,
        )

    dialog = ft.AlertDialog(
        modal=False,
        title=ft.Text("Notificaciones", size=16, color=Colors.TEXT_PRIMARY),
        bgcolor=Colors.SURFACE,
        content=ft.Container(width=420, content=contenido),
        actions=[
            ft.TextButton(content=ft.Text("Cerrar", color=Colors.TEXT_SECONDARY), on_click=handle_cerrar),
        ],
    )

    page.show_dialog(dialog)
