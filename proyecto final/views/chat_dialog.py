"""
Diálogo de chat entre dos usuarios sobre un carro específico (comprador
interesado <-> vendedor, o ganador de la subasta <-> vendedor para coordinar
la entrega). Se invoca desde el panel de detalle de una subasta o desde
'Mis Carros' (para que el vendedor revise sus conversaciones).

Uso: mostrar_chat(page, sistema, usuario_actual, carro_dict, otro_usuario_id, on_change)
Esta función arma el diálogo Y lo muestra (page.show_dialog) — el llamador
no necesita hacer nada más.
"""

import flet as ft
from theme import Colors


def _burbuja(mensaje, es_mio: bool) -> ft.Row:
    hora = (mensaje.fecha_hora or "")[11:16]
    burbuja = ft.Container(
        content=ft.Column(
            [
                ft.Text(mensaje.texto, size=13,
                         color=Colors.TEXT_ON_ACCENT if es_mio else Colors.TEXT_PRIMARY),
                ft.Text(hora, size=10,
                         color=Colors.TEXT_ON_ACCENT if es_mio else Colors.TEXT_SECONDARY),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.END if es_mio else ft.CrossAxisAlignment.START,
        ),
        bgcolor=Colors.ACCENT_INDIGO if es_mio else Colors.SURFACE_ALT,
        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        border_radius=12,
        width=320,
    )
    return ft.Row([burbuja], alignment=ft.MainAxisAlignment.END if es_mio else ft.MainAxisAlignment.START)


def mostrar_chat(page: ft.Page, sistema, usuario_actual, carro: dict, otro_usuario_id: str, on_change=None) -> None:
    otro = sistema.usuarios.get(otro_usuario_id)
    otro_nombre = otro.nombre if otro else "Usuario"

    # Abrir el chat marca como leído lo que me escribieron — y eso se
    # persiste de inmediato junto con el resto del estado.
    sistema.marcar_conversacion_leida(carro["id"], usuario_actual.id, otro_usuario_id, lector_id=usuario_actual.id)
    if on_change:
        on_change()

    mensajes_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=320)
    input_field = ft.TextField(
        hint_text="Escribe un mensaje...",
        hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
        bgcolor=Colors.SURFACE,
        border_color=Colors.BORDER,
        border_radius=8,
        color=Colors.TEXT_PRIMARY,
        height=42,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        text_size=13,
        expand=True,
    )
    feedback = ft.Text("", size=12, color="#E26A6A")

    def refrescar():
        conversacion = sistema.obtener_conversacion(carro["id"], usuario_actual.id, otro_usuario_id)
        if conversacion:
            mensajes_column.controls = [_burbuja(m, m.id_remitente == usuario_actual.id) for m in conversacion]
        else:
            mensajes_column.controls = [
                ft.Text("Todavía no hay mensajes. Escribe el primero.", size=12, color=Colors.TEXT_SECONDARY)
            ]
        page.update()

    def handle_enviar(e):
        texto = (input_field.value or "").strip()
        if not texto:
            return
        ok, resultado = sistema.enviar_mensaje(carro["id"], usuario_actual.id, otro_usuario_id, texto)
        if not ok:
            feedback.value = resultado
            page.update()
            return
        feedback.value = ""
        input_field.value = ""
        if on_change:
            on_change()
        refrescar()

    input_field.on_submit = handle_enviar

    def handle_cerrar(e):
        page.pop_dialog()
        page.update()

    dialog = ft.AlertDialog(
        modal=False,
        title=ft.Text(f'Chat sobre {carro["marca"]} {carro["modelo"]}', size=16, color=Colors.TEXT_PRIMARY),
        bgcolor=Colors.SURFACE,
        content=ft.Container(
            width=420,
            content=ft.Column(
                [
                    ft.Text(f"Con {otro_nombre}", size=12, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=10),
                    mensajes_column,
                    ft.Container(height=8),
                    ft.Row(
                        [
                            input_field,
                            ft.ElevatedButton(
                                content=ft.Text("Enviar", size=13),
                                bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=handle_enviar,
                            ),
                        ],
                        spacing=8,
                    ),
                    feedback,
                ],
                spacing=0,
                tight=True,
            ),
        ),
        actions=[
            ft.TextButton(content=ft.Text("Cerrar", color=Colors.TEXT_SECONDARY), on_click=handle_cerrar),
        ],
    )

    refrescar()
    page.show_dialog(dialog)
