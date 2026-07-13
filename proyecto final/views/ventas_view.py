"""
Pestaña 'VENTAS'.

Historial de subastas YA CERRADAS de este usuario como vendedor: vendidas
(con comprador y comisión de plataforma) y no vendidas (no alcanzaron la
reserva o no tuvieron pujas).

Además incluye:
- 'Mis Gastos': historial de las compras cerradas de este usuario como
  comprador (mismo dato que alimenta la sección de 'Compras ganadas' en
  Subastas Activas, mostrado acá con foco en el gasto en vez de en
  coordinar la entrega).
- Un resumen de balance financiero (ingresos netos vs. gastos) que combina
  ambos lados, y un botón para exportar todo el detalle a un archivo Excel
  con un gráfico de ingresos vs. egresos por mes (ver
  sistema.generar_reporte_excel_usuario en backend/sistema.py).
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, estado_badge, empty_state, auto_imagen
from views.detalle_subasta_dialog import mostrar_detalle_subasta


def _fila_venta(c: dict, sistema, usuario_actual, page, on_change) -> ft.Container:
    if c["estado_subasta"] == "vendido":
        entrega_txt = (
            " · Entrega confirmada ✓" if c.get("entrega_confirmada")
            else " · Entrega pendiente de confirmar por el comprador"
        )
        detalle = (f'Vendido a {c["comprador_nombre"]} por {money(c["precio_final_venta"])} · '
                   f'Comisión plataforma: {money(c["comision"])}{entrega_txt}')
    else:
        detalle = "No se vendió (sin pujas o no se alcanzó el precio de reserva)."

    return card(
        ft.Row(
            [
                auto_imagen(c.get("imagen"), width=90, height=68),
                ft.Column(
                    [
                        ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                 size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                        ft.Text(detalle, size=12, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=2,
                    expand=True,
                ),
                estado_badge(c["estado_subasta"]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=16,
        ),
        padding=16,
        on_click=lambda e: mostrar_detalle_subasta(page, sistema, usuario_actual, c, on_change),
    )


def _fila_gasto(c: dict, sistema, usuario_actual, page, on_change) -> ft.Container:
    """Fila de la sección 'Mis Gastos': una compra ya cerrada donde este
    usuario fue el comprador. Reutiliza el mismo dict que alimenta 'Compras
    ganadas' en Subastas Activas (obtener_mis_compras_ganadas), pero acá el
    foco es el gasto — no hay botones de acción, solo el detalle al hacer clic."""
    entregado = c.get("entrega_confirmada", False)
    badge_entrega = ft.Container(
        content=ft.Text("ENTREGADO" if entregado else "PENDIENTE DE ENTREGA", size=11,
                         weight=ft.FontWeight.W_600, color=Colors.BACKGROUND),
        bgcolor="#7ED957" if entregado else Colors.TEXT_SECONDARY,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=6,
    )

    return card(
        ft.Row(
            [
                auto_imagen(c.get("imagen"), width=90, height=68),
                ft.Column(
                    [
                        ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                 size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                        ft.Text(f'Comprado a {c["vendedor_nombre"]} por {money(c["precio_final_venta"])}',
                                 size=12, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=2,
                    expand=True,
                ),
                badge_entrega,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=16,
        ),
        padding=16,
        on_click=lambda e: mostrar_detalle_subasta(page, sistema, usuario_actual, c, on_change),
    )


def _nombre_archivo_reporte(usuario_actual) -> str:
    """Nombre de archivo sugerido para el diálogo de guardado: nombre del
    usuario 'saneado' (sin espacios ni caracteres raros) + su id, para que
    dos usuarios con el mismo nombre no se pisen el archivo por accidente."""
    base = "".join(ch if ch.isalnum() else "_" for ch in usuario_actual.nombre.strip())
    return f"reporte_financiero_{base}_{usuario_actual.id}.xlsx"


def ventas_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None,
                 on_account_click=None, on_search=None, valor_busqueda="",
                 on_messages_click=None) -> ft.Container:
    ventas = sistema.obtener_mis_ventas(usuario_actual.id)
    gastos = sistema.obtener_mis_compras_ganadas(usuario_actual.id)
    balance = sistema.obtener_resumen_financiero_usuario(usuario_actual.id)

    # --- Exportar a Excel: FilePicker.save_file() deja elegir dónde guardar
    # (mismo Service de Flet que ft.FilePicker.pick_files, ya usado en
    # mis_carros_view.py / perfil_view.py — también se autorregistra por
    # contexto en esta versión de Flet y no necesita ir a page.overlay). ---
    reporte_file_picker = ft.FilePicker()
    reporte_feedback = ft.Text("", size=12)

    async def handle_descargar_reporte(e):
        ruta_elegida = await reporte_file_picker.save_file(
            dialog_title="Guardar reporte financiero",
            file_name=_nombre_archivo_reporte(usuario_actual),
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
        )
        if not ruta_elegida:
            return  # el usuario cerró el diálogo sin elegir dónde guardar

        ok, resultado = sistema.generar_reporte_excel_usuario(usuario_actual.id, ruta_elegida)
        if not ok:
            reporte_feedback.value = resultado
            reporte_feedback.color = "#E26A6A"
        else:
            reporte_feedback.value = f"Reporte guardado en: {resultado}"
            reporte_feedback.color = Colors.ACCENT_TEAL
        page.update()

    descargar_reporte_btn = ft.OutlinedButton(
        content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, size=16), ft.Text("Descargar reporte Excel", size=13)], spacing=6),
        on_click=handle_descargar_reporte,
    )

    # --- Balance financiero: combina ingresos (como vendedor, ya neto de
    # comisión) y egresos (como comprador) en un único panorama. ---
    balance_row = ft.Row(
        [
            card(
                ft.Column([
                    ft.Text("INGRESOS NETOS", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(money(balance["ingresos_netos"]), size=22, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    ft.Text("Ya descontada la comisión de plataforma", size=11, color=Colors.TEXT_MUTED),
                ], spacing=0),
                expand=True,
            ),
            card(
                ft.Column([
                    ft.Text("TOTAL GASTADO", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(money(balance["total_egresos"]), size=22, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    ft.Text(f'{balance["num_compras"]} compra(s) cerrada(s)', size=11, color=Colors.TEXT_MUTED),
                ], spacing=0),
                expand=True,
            ),
            card(
                ft.Column([
                    ft.Text("BALANCE NETO", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(money(balance["balance_neto"]), size=22, weight=ft.FontWeight.BOLD,
                             color="#7ED957" if balance["balance_neto"] >= 0 else "#E26A6A"),
                    ft.Text("Ingresos netos − gastos", size=11, color=Colors.TEXT_MUTED),
                ], spacing=0),
                expand=True,
            ),
        ],
        spacing=Sizes.GAP,
    )

    # --- Sección Ventas (como vendedor) ---
    vendidos = [v for v in ventas if v["estado_subasta"] == "vendido"]
    total_vendido = sum(v["precio_final_venta"] for v in vendidos)
    total_comision = sum(v["comision"] for v in vendidos)

    resumen_ventas_row = ft.Row(
        [
            card(
                ft.Column([
                    ft.Text("AUTOS VENDIDOS", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(str(len(vendidos)), size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                expand=True,
            ),
            card(
                ft.Column([
                    ft.Text("TOTAL VENDIDO", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(money(total_vendido), size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                expand=True,
            ),
            card(
                ft.Column([
                    ft.Text("COMISIÓN PAGADA", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(money(total_comision), size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                expand=True,
            ),
        ],
        spacing=Sizes.GAP,
    )

    lista_ventas = [_fila_venta(c, sistema, usuario_actual, page, on_change) for c in ventas] if ventas else [
        empty_state("Todavía no tienes subastas cerradas como vendedor.")
    ]

    # --- Sección Mis Gastos (como comprador) ---
    resumen_gastos_row = ft.Row(
        [
            card(
                ft.Column([
                    ft.Text("AUTOS COMPRADOS", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(str(balance["num_compras"]), size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                expand=True,
            ),
            card(
                ft.Column([
                    ft.Text("TOTAL GASTADO", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text(money(balance["total_egresos"]), size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                expand=True,
            ),
        ],
        spacing=Sizes.GAP,
    )

    lista_gastos = [_fila_gasto(c, sistema, usuario_actual, page, on_change) for c in gastos] if gastos else [
        empty_state("Todavía no tienes compras cerradas como comprador.")
    ]

    body = ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Ventas y Gastos", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                            ft.Text("Balance completo de tus movimientos en la plataforma.",
                                     size=13, color=Colors.TEXT_SECONDARY),
                        ],
                        spacing=2,
                    ),
                    descargar_reporte_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            reporte_feedback,
            ft.Container(height=Sizes.GAP),
            balance_row,

            ft.Container(height=Sizes.GAP * 1.5),
            ft.Divider(color=Colors.BORDER, height=1),
            ft.Container(height=Sizes.GAP),

            ft.Text("Ventas (como vendedor)", size=15, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text("Historial de tus subastas ya cerradas.", size=13, color=Colors.TEXT_SECONDARY),
            ft.Container(height=Sizes.GAP),
            resumen_ventas_row,
            ft.Container(height=Sizes.GAP),
            *[item for c in lista_ventas for item in (c, ft.Container(height=12))],

            ft.Container(height=Sizes.GAP),
            ft.Divider(color=Colors.BORDER, height=1),
            ft.Container(height=Sizes.GAP),

            ft.Text("Mis Gastos (como comprador)", size=15, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text("Historial de tus compras ya cerradas.", size=13, color=Colors.TEXT_SECONDARY),
            ft.Container(height=Sizes.GAP),
            resumen_gastos_row,
            ft.Container(height=Sizes.GAP),
            *[item for c in lista_gastos for item in (c, ft.Container(height=12))],
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "VENTAS", body, sistema=sistema, on_nav_click=on_nav_click,
                       on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda,
                       on_messages_click=on_messages_click)
