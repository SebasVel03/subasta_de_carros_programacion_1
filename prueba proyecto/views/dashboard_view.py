import flet as ft
import flet_charts as fch
from theme import Colors, Sizes, card
from views.shared import page_shell, money as _money


def _stat_card(label: str, value: str, subtitle: str) -> ft.Container:
    return card(
        ft.Column(
            [
                ft.Text(label, size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                ft.Container(height=10),
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Container(height=6),
                ft.Text(subtitle, size=12, color=Colors.TEXT_SECONDARY),
            ],
            spacing=0,
        ),
        expand=True,
    )


def _chart_placeholder(mensaje: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(mensaje, size=13, color=Colors.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
        height=320,
        alignment=ft.Alignment.CENTER,
    )


def _income_chart(ingresos_por_mes: dict) -> ft.Container:
    meses = list(ingresos_por_mes.keys())
    valores = list(ingresos_por_mes.values())

    if len(meses) < 2:
        chart_content = _chart_placeholder(
            "Todavía no hay suficiente historial de ventas\npara graficar ingresos por mes."
        )
    else:
        max_val = max(valores)
        chart = fch.LineChart(
            data_series=[
                fch.LineChartData(
                    points=[fch.LineChartDataPoint(i, v) for i, v in enumerate(valores)],
                    stroke_width=2,
                    color=Colors.LINE_WHITE,
                    curved=False,
                    rounded_stroke_cap=True,
                )
            ],
            horizontal_grid_lines=fch.ChartGridLines(color=Colors.BORDER, width=1),
            left_axis=fch.ChartAxis(label_size=60),
            bottom_axis=fch.ChartAxis(
                label_size=24,
                labels=[fch.ChartAxisLabel(value=i, label=m) for i, m in enumerate(meses)],
            ),
            min_y=0,
            max_y=max_val * 1.15,
            min_x=0,
            max_x=len(valores) - 1,
            tooltip=fch.LineChartTooltip(bgcolor=Colors.SURFACE_ALT),
            expand=True,
        )
        chart_content = ft.Container(chart, height=320)

    return card(
        ft.Column(
            [
                ft.Text("GRAFICO DE INGRESOS", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                ft.Container(height=10),
                chart_content,
            ],
            spacing=0,
        ),
        expand=True,
    )


def _frequent_bidders(bidders: list) -> ft.Container:
    if not bidders:
        contenido = [_chart_placeholder("Todavía no hay pujas registradas\nen la plataforma.")]
    else:
        contenido = []
        for b in bidders:
            contenido.append(
                ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color=Colors.TEXT_PRIMARY, size=18),
                            bgcolor=Colors.SURFACE_ALT,
                            radius=18,
                        ),
                        ft.Column(
                            [
                                ft.Text(b["nombre"], size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                                ft.Text(b["email"], size=12, color=Colors.TEXT_SECONDARY),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        ft.Text(f'{b["cantidad_pujas"]} pujas', size=12, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=12,
                )
            )
            contenido.append(ft.Container(height=14))

    return card(
        ft.Column(
            [
                ft.Text("SUBASTADORES FRECUENTES", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                ft.Container(height=14),
                *contenido,
            ],
            spacing=0,
        ),
        expand=True,
    )


def _net_movements_chart(actividad_por_mes: dict) -> ft.Container:
    meses = list(actividad_por_mes.keys())
    valores = list(actividad_por_mes.values())

    if len(meses) < 2:
        chart_content = _chart_placeholder(
            "Todavía no hay suficiente actividad de pujas\npara graficar por mes."
        )
    else:
        max_val = max(valores)
        groups = [
            fch.BarChartGroup(
                x=i,
                rods=[fch.BarChartRod(from_y=0, to_y=v, width=18, color=Colors.LINE_WHITE, border_radius=2)],
            )
            for i, v in enumerate(valores)
        ]
        chart = fch.BarChart(
            groups=groups,
            horizontal_grid_lines=fch.ChartGridLines(color=Colors.BORDER, width=1),
            left_axis=fch.ChartAxis(label_size=40),
            bottom_axis=fch.ChartAxis(
                label_size=24,
                labels=[fch.ChartAxisLabel(value=i, label=m) for i, m in enumerate(meses)],
            ),
            min_y=0,
            max_y=max_val * 1.15,
            tooltip=fch.BarChartTooltip(bgcolor=Colors.SURFACE_ALT),
            expand=True,
        )
        chart_content = ft.Container(chart, height=320)

    return card(
        ft.Column(
            [
                ft.Text("ACTIVIDAD DE PUJAS", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                ft.Container(height=10),
                chart_content,
            ],
            spacing=0,
        ),
        expand=True,
    )


def _closing_soon_table(subastas: list) -> ft.Container:
    header = ft.Row(
        [
            ft.Text("Carro", size=12, color=Colors.TEXT_SECONDARY, expand=True),
            ft.Text("Pujas", size=12, color=Colors.TEXT_SECONDARY, width=60, text_align=ft.TextAlign.RIGHT),
            ft.Text("Cierra en", size=12, color=Colors.TEXT_SECONDARY, width=90, text_align=ft.TextAlign.RIGHT),
        ]
    )

    rows = [header, ft.Divider(color=Colors.BORDER, height=1)]

    if not subastas:
        rows.append(
            ft.Container(
                content=ft.Text("No hay subastas activas en este momento.", size=13, color=Colors.TEXT_SECONDARY),
                padding=ft.Padding.symmetric(vertical=14),
            )
        )
    else:
        for s in subastas:
            horas = s["horas_restantes"]
            etiqueta_tiempo = f"{horas:.0f} h" if horas < 48 else f"{horas / 24:.0f} d"
            rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(s["carro"], size=13, color=Colors.TEXT_PRIMARY, expand=True),
                            ft.Text(str(s["num_pujas"]), size=13, color=Colors.TEXT_PRIMARY,
                                    width=60, text_align=ft.TextAlign.RIGHT),
                            ft.Text(etiqueta_tiempo, size=13, color=Colors.ACCENT_TEAL,
                                    width=90, text_align=ft.TextAlign.RIGHT),
                        ]
                    ),
                    padding=ft.Padding.symmetric(vertical=10),
                )
            )

    return card(
        ft.Column(
            [
                ft.Text("SUBASTAS POR CERRAR PRONTO", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                ft.Container(height=14),
                *rows,
            ],
            spacing=0,
        ),
        expand=True,
    )


# ---------------------------------------------------------------------------
# Vista principal
# ---------------------------------------------------------------------------

def dashboard_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None, on_account_click=None, on_search=None, valor_busqueda="") -> ft.Container:
    """
    sistema: instancia de backend.AdministradorCompraVenta ya cargada.
    usuario_actual: instancia de backend.Usuario que inició sesión.
    on_change: no se usa en esta vista (no hay acciones que mutan datos aquí),
    se acepta solo para que las 5 vistas tengan la misma firma.
    """

    resumen = sistema.obtener_resumen_dashboard(usuario_actual.id)
    bidders = sistema.obtener_subastadores_frecuentes()
    por_cerrar = sistema.obtener_subastas_por_cerrar()
    ingresos_mensuales = sistema.obtener_ingresos_mensuales()
    actividad_mensual = sistema.obtener_actividad_pujas_mensual()

    body = ft.Column(
        [
            ft.Row(
                [
                    _stat_card("GANANCIAS", _money(resumen["ganancias"]), "Autos que vendiste"),
                    _stat_card("GASTADO", _money(resumen["gastado"]), "Autos que compraste"),
                    _stat_card("SUBASTAS ACTIVAS", str(resumen["subastas_activas_pendientes"]),
                               "En toda la plataforma"),
                ],
                spacing=Sizes.GAP,
            ),
            ft.Container(height=Sizes.GAP),
            ft.Row(
                [_income_chart(ingresos_mensuales), _frequent_bidders(bidders)],
                spacing=Sizes.GAP,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(height=Sizes.GAP),
            ft.Row(
                [_net_movements_chart(actividad_mensual), _closing_soon_table(por_cerrar)],
                spacing=Sizes.GAP,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "RESUMEN", body, on_nav_click=on_nav_click, on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda)
