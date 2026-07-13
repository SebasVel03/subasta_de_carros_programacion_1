"""
Pestaña 'REVISIÓN' (solo visible para usuarios con rol 'admin').

Muestra la cola de subastas en estado 'pendiente_revision' con todo lo que
un experto necesita para validar el vehículo: foto, especificaciones técnicas,
condición declarada, descripción de daños, si los documentos están en regla,
y datos del vendedor. Desde aquí se aprueba o se rechaza (con motivo).
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, empty_state, auto_imagen


def _dato(etiqueta: str, valor: str) -> ft.Column:
    return ft.Column(
        [
            ft.Text(etiqueta, size=11, color=Colors.TEXT_SECONDARY),
            ft.Text(valor, size=13, color=Colors.TEXT_PRIMARY),
        ],
        spacing=2,
    )


def _fila_revision(c: dict, sistema, page, on_change) -> ft.Container:
    motivo_field = ft.TextField(
        hint_text="Motivo del rechazo (opcional)",
        width=320, height=42, text_size=12,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
    )
    feedback = ft.Text("", size=12)

    def handle_aprobar(e):
        ok, resultado = sistema.aprobar_subasta(c["id"])
        if not ok:
            feedback.value = resultado
            feedback.color = "#E26A6A"
            page.update()
            return
        if on_change:
            on_change()

    def handle_rechazar(e):
        ok, resultado = sistema.rechazar_subasta(c["id"], motivo_field.value or "")
        if not ok:
            feedback.value = resultado
            feedback.color = "#E26A6A"
            page.update()
            return
        if on_change:
            on_change()

    especificaciones_txt = ", ".join(f"{k}: {v}" for k, v in c["especificaciones"].items()) or "—"
    extras_txt = ", ".join(c["extras"]) or "—"
    documentos_txt = "✓ En regla" if c["documentos_en_regla"] else "✗ Pendientes / sin confirmar"

    return card(
        ft.Column(
            [
                ft.Row(
                    [
                        auto_imagen(c.get("imagen"), width=140, height=100),
                        ft.Column(
                            [
                                ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                         size=16, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                ft.Text(f'Vendedor: {c["vendedor_nombre"]} '
                                        f'({"verificado" if c["vendedor_verificado"] else "NO verificado"}, '
                                        f'{c["vendedor_reputacion"]}⭐)',
                                         size=12, color=Colors.TEXT_SECONDARY),
                                ft.Container(height=8),
                                ft.Row(
                                    [
                                        _dato("Kilometraje", f'{c["kilometraje"]:,} km'),
                                        _dato("Precio base", money(c["precio_base"])),
                                        _dato("Precio reserva", money(c["precio_reserva"])),
                                        _dato("Duración", f'{c["duracion_dias"]} días'),
                                    ],
                                    spacing=24,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                    ],
                    spacing=16,
                ),
                ft.Container(height=12),
                ft.Divider(color=Colors.BORDER, height=1),
                ft.Container(height=12),
                ft.Row(
                    [
                        _dato("Especificaciones", especificaciones_txt),
                        _dato("Extras", extras_txt),
                    ],
                    spacing=24,
                ),
                ft.Container(height=8),
                ft.Row(
                    [
                        _dato("Condición declarada", c["condicion_general"] or "No especificada"),
                        _dato("Documentos", documentos_txt),
                    ],
                    spacing=24,
                ),
                ft.Container(height=8),
                _dato("Descripción de daños", c["descripcion_danos"] or "Sin daños reportados"),
                ft.Container(height=12),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            content=ft.Text("Aprobar y publicar"),
                            bgcolor="#7ED957", color=Colors.BACKGROUND,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=handle_aprobar,
                        ),
                        motivo_field,
                        ft.ElevatedButton(
                            content=ft.Text("Rechazar"),
                            bgcolor="#E26A6A", color=Colors.BACKGROUND,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=handle_rechazar,
                        ),
                    ],
                    spacing=12,
                ),
                feedback,
            ],
            spacing=0,
        ),
        padding=20,
    )


def revision_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None,
                   on_account_click=None, on_search=None, valor_busqueda="",
                   on_messages_click=None) -> ft.Container:
    if not usuario_actual or usuario_actual.rol != "admin":
        body = empty_state("Esta sección es solo para administradores/expertos de la plataforma.")
        return page_shell(usuario_actual, "REVISIÓN", body, sistema=sistema, on_nav_click=on_nav_click,
                           on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda,
                           on_messages_click=on_messages_click)

    pendientes = sistema.obtener_subastas_pendientes_revision(excluir_vendedor_id=usuario_actual.id)

    lista = [_fila_revision(c, sistema, page, on_change) for c in pendientes] if pendientes else [
        empty_state("No hay subastas pendientes de revisión por ahora.")
    ]

    body = ft.Column(
        [
            ft.Text("Revisión de Subastas", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text("Valida el vehículo antes de que la subasta salga al público.",
                     size=13, color=Colors.TEXT_SECONDARY),
            ft.Container(height=Sizes.GAP),
            *[item for c in lista for item in (c, ft.Container(height=12))],
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "REVISIÓN", body, sistema=sistema, on_nav_click=on_nav_click,
                       on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda,
                       on_messages_click=on_messages_click)
