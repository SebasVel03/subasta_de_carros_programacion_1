import flet as ft


def main(page: ft.Page):
    page.title = "App Subastas"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800

    BG_COLOR = "#0e111d"
    CARD_COLOR = "#1a1c30"
    TEXT_MAIN = ft.Colors.WHITE
    TEXT_MUTED = ft.Colors.WHITE70
    ACCENT_COLOR = "#3b82f6"

    email_field = ft.TextField(
        hint_text="correoelectrónico@dominio.com",
        width=400,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        border_radius=8,
    )
    error_message = ft.Text("", color=ft.Colors.RED, size=12)

    def show_login():
        page.views.clear()
        page.views.append(login_view())
        page.update()

    def show_dashboard():
        page.views.clear()
        page.views.append(dashboard_view())
        page.update()

    def intentar_login(_e):
        if not email_field.value or email_field.value.strip() == "":
            error_message.value = "Por favor, ingresa un correo electrónico válido."
            page.update()
        else:
            error_message.value = ""
            show_dashboard()

    def login_view():
        return ft.View(
            route="/login",
            bgcolor=BG_COLOR,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("subasta", size=60, weight=ft.FontWeight.W_300, color=TEXT_MAIN),
                        ft.Container(height=20),
                        ft.Text("Crea una cuenta / Inicia sesión", size=20, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Text("Ingresa tu correo electrónico para registrarte en esta app", color=TEXT_MUTED),
                        ft.Container(height=20),
                        email_field,
                        error_message,
                        ft.Container(height=10),
                        ft.Button(
                            content=ft.Text("Continuar con correo electrónico"),
                            width=400,
                            bgcolor=ft.Colors.BLACK,
                            color=ft.Colors.WHITE,
                            on_click=intentar_login,
                        ),
                        ft.Container(height=10),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text("si ya tienes cuenta,", color=TEXT_MUTED),
                                ft.TextButton(content=ft.Text("inicia sesion"), on_click=lambda _e: show_dashboard()),
                            ],
                        ),
                        ft.Container(height=40),
                        ft.Text("Al hacer clic en Continuar aceptas nuestros Términos de servicio y la", color=TEXT_MUTED, size=12),
                        ft.Text("Política de privacidad", color=TEXT_MUTED, size=12),
                    ],
                )
            ],
        )

    def card_container(content, width=None, height=None, expand: bool | int = False):
        return ft.Container(
            content=content,
            bgcolor=CARD_COLOR,
            border_radius=10,
            padding=20,
            width=width,
            height=height,
            expand=expand,
        )

    def dashboard_view():
        nav_bar = ft.Container(
            padding=20,
            bgcolor=BG_COLOR,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("APP SUBASTAS", size=20, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Row(
                        spacing=20,
                        controls=[
                            ft.Text("RESUMEN", color=TEXT_MAIN, weight=ft.FontWeight.BOLD),
                            ft.Text("MIS CARROS", color=TEXT_MUTED),
                            ft.Text("EXPLORAR SUBASTAS", color=TEXT_MUTED),
                            ft.Text("SUBASTAS ACTIVAS", color=TEXT_MUTED),
                            ft.Text("VENTAS", color=TEXT_MUTED),
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.TextField(hint_text="Buscar...", width=200, height=40, text_size=12, border_radius=20, content_padding=10),
                            ft.CircleAvatar(bgcolor=ft.Colors.GREY_800, radius=15, content=ft.Icon("person", size=15)),
                        ]
                    ),
                ],
            ),
        )

        summary_cards = ft.Row(
            spacing=20,
            controls=[
                card_container(ft.Column([
                    ft.Text("GANANCIAS", size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text("$45 678,90", size=30, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text("+20 % mes a mes", size=12, color=ft.Colors.GREEN_400),
                ]), expand=True),
                card_container(ft.Column([
                    ft.Text("GASTADO", size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text("2405$", size=30, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text("+33% mes a mes", size=12, color=ft.Colors.RED_400),
                ]), expand=True),
                card_container(ft.Column([
                    ft.Text("SUBASTAS ACTIVAS PENDIENTES", size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text("10 353", size=30, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text("-8% mes a mes", size=12, color=TEXT_MUTED),
                ]), expand=True),
            ],
        )

        middle_section = ft.Row(
            spacing=20,
            controls=[
                card_container(ft.Column([
                    ft.Text("GRÁFICO DE INGRESOS", size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0.5, 0.5),
                        content=ft.Icon(name=ft.icons.SHOW_CHART, size=100, color=ft.Colors.WHITE24),
                    ),
                ]), expand=2, height=350),
                card_container(ft.Column([
                    ft.Text("SUBASTADORES FRECUENTES", size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.ListView(expand=True, spacing=10, controls=[
                        ft.ListTile(leading=ft.CircleAvatar(content=ft.Text("E")), title=ft.Text("Elena", size=14, color=TEXT_MAIN), subtitle=ft.Text("elena@dominio.com", size=12, color=TEXT_MUTED)),
                        ft.ListTile(leading=ft.CircleAvatar(content=ft.Text("O")), title=ft.Text("Oscar", size=14, color=TEXT_MAIN), subtitle=ft.Text("oscar@dominio.com", size=12, color=TEXT_MUTED)),
                        ft.ListTile(leading=ft.CircleAvatar(content=ft.Text("D")), title=ft.Text("Daniel", size=14, color=TEXT_MAIN), subtitle=ft.Text("daniel@dominio.com", size=12, color=TEXT_MUTED)),
                    ]),
                ]), expand=1, height=350),
            ],
        )

        return ft.View(
            route="/dashboard",
            bgcolor=BG_COLOR,
            padding=0,
            controls=[
                nav_bar,
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        spacing=20,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            summary_cards,
                            middle_section,
                        ],
                    ),
                ),
            ],
        )

    def route_change(_e):
        page.views.clear()
        try:
            if page.route == "/dashboard":
                page.views.append(dashboard_view())
            else:
                page.views.append(login_view())
        except Exception as ex:
            print(f"Error cargando la vista: {ex}")
        page.update()

    page.on_route_change = route_change
    show_login()


if __name__ == "__main__":
    ft.run(main)