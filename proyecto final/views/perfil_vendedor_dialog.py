"""
Diálogo de solo lectura con el perfil público de un vendedor (o cualquier
usuario dueño de un carro), para que un comprador pueda evaluar si es
confiable antes de pujar. Se abre desde el panel de detalle de una subasta
(views/detalle_subasta_dialog.py), al hacer clic en la fila con el nombre
del vendedor.

Incluye las reseñas que recibió como vendedor (ver sistema.calificar_vendedor
/ obtener_calificaciones_usuario en backend/sistema.py) -- son las que
alimentan perfil["reputacion"] de acá arriba.

No incluye acciones que mutan datos (no recibe on_change) — es puramente
informativo, igual que account_panel.py en cuanto a estructura de diálogo.

Uso: mostrar_perfil_vendedor(page, sistema, id_vendedor)
"""

import flet as ft
from theme import Colors
from views.shared import avatar_imagen

MAX_RESENAS_MOSTRADAS = 5


def _stat(etiqueta: str, valor: str) -> ft.Column:
    return ft.Column(
        [
            ft.Text(valor, size=20, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text(etiqueta, size=11, color=Colors.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
        ],
        spacing=2,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _fila_resena(c: dict) -> ft.Column:
    estrellas_txt = "⭐" * c["estrellas"] + "☆" * (5 - c["estrellas"])
    controles: list[ft.Control] = [
        ft.Row(
            [
                ft.Text(c["calificador_nombre"], size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                ft.Text(estrellas_txt, size=12, color=Colors.ACCENT_TEAL),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
    ]
    if c["comentario"]:
        controles.append(ft.Text(c["comentario"], size=12, color=Colors.TEXT_SECONDARY))
    return ft.Column(controles, spacing=2)


def mostrar_perfil_vendedor(page: ft.Page, sistema, id_vendedor: str) -> None:
    perfil = sistema.obtener_perfil_publico_usuario(id_vendedor)

    def handle_cerrar(e):
        page.pop_dialog()
        page.update()

    if not perfil:
        # Vendedor con id roto / borrado — mismo criterio tolerante que el
        # resto del proyecto (ej. main.py al restaurar sesión), no se rompe
        # la UI, solo se avisa.
        dialog = ft.AlertDialog(
            modal=False,
            bgcolor=Colors.SURFACE,
            content=ft.Text("No se pudo cargar la información de este vendedor.",
                             size=13, color=Colors.TEXT_SECONDARY),
            actions=[ft.TextButton(content=ft.Text("Cerrar", color=Colors.TEXT_SECONDARY), on_click=handle_cerrar)],
        )
        page.show_dialog(dialog)
        return

    verificado_txt = "✓ Cuenta verificada" if perfil["verificado"] else "✗ Cuenta no verificada"
    verificado_color = "#7ED957" if perfil["verificado"] else "#E26A6A"

    calificaciones = sistema.obtener_calificaciones_usuario(id_vendedor)
    if calificaciones:
        resenas_controles: list[ft.Control] = []
        for c in calificaciones[:MAX_RESENAS_MOSTRADAS]:
            resenas_controles.append(_fila_resena(c))
            resenas_controles.append(ft.Container(height=10))
        if len(calificaciones) > MAX_RESENAS_MOSTRADAS:
            resenas_controles.append(
                ft.Text(f"+ {len(calificaciones) - MAX_RESENAS_MOSTRADAS} reseña(s) más",
                         size=11, color=Colors.TEXT_MUTED)
            )
    else:
        resenas_controles = [ft.Text("Todavía no tiene reseñas.", size=12, color=Colors.TEXT_SECONDARY)]

    contenido = ft.Column(
        [
            ft.Row(
                [
                    avatar_imagen(perfil["foto_perfil"], size=64),
                    ft.Column(
                        [
                            ft.Text(perfil["nombre"], size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                            ft.Text(f'{perfil["reputacion"]} ⭐ de reputación', size=13, color=Colors.TEXT_SECONDARY),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=16,
            ),
            ft.Container(height=14),
            ft.Container(
                content=ft.Text(verificado_txt, size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_ON_ACCENT),
                bgcolor=verificado_color,
                padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                border_radius=6,
            ),
            ft.Container(height=18),
            ft.Divider(color=Colors.BORDER, height=1),
            ft.Container(height=18),
            ft.Row(
                [
                    _stat("Autos vendidos", str(perfil["autos_vendidos"])),
                    _stat("Autos publicados", str(perfil["autos_publicados"])),
                    _stat("Subastas activas", str(perfil["subastas_activas"])),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
            ft.Container(height=18),
            ft.Text(f'Miembro desde {(perfil["fecha_registro"] or "")[:10]}', size=12, color=Colors.TEXT_MUTED),
            ft.Container(height=18),
            ft.Divider(color=Colors.BORDER, height=1),
            ft.Container(height=18),
            ft.Text("Reseñas", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Container(height=10),
            *resenas_controles,
        ],
        spacing=0,
        tight=True,
    )

    dialog = ft.AlertDialog(
        modal=False,
        scrollable=True,
        bgcolor=Colors.SURFACE,
        content=ft.Container(width=380, content=contenido),
        actions=[
            ft.TextButton(content=ft.Text("Cerrar", color=Colors.TEXT_SECONDARY), on_click=handle_cerrar),
        ],
    )

    page.show_dialog(dialog)
