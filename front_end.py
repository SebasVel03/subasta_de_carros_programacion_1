import flet as ft
from typing import cast


def main(page: ft.Page):
    page.title = "App Subastas"
    bg_color = "#0e111d"
    card_color = "#1a1c30"
    accent_color = "#3b82f6"

    page.bgcolor = bg_color
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK

    def card_container(content, width=None, height=None, expand: bool | int = False):
        return ft.Container(
            content=content,
            width=width,
            height=height,
            expand=expand,
            bgcolor=card_color,
            border_radius=16,
            padding=20,
            margin=10,
        )

    email_field = ft.TextField(
        hint_text="correoelectrónico@dominio.com",
        width=400,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        border_radius=8,
    )
    error_message = ft.Text("", color=ft.Colors.RED, size=12)

    def intentar_login(e):
        if not email_field.value or email_field.value.strip() == "":
            error_message.value = "Por favor, ingresa un correo electrónico válido."
            page.update()
        else:
            error_message.value = ""
            page.go("/dashboard")

    def login_view():
        login_form = ft.Column(
            controls=[
                ft.Text(
                    "Subastas de Carros",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Inicia sesión o regístrate",
                    color=ft.Colors.WHITE70,
                ),
                email_field,
                error_message,
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Entrar",
                            on_click=intentar_login,
                        ),
                        ft.TextButton(
                            "Crear cuenta",
                            on_click=lambda e: page.go("/dashboard"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.View(
            route="/login",
            controls=[
                ft.Container(
                    content=login_form,
                    alignment=ft.Alignment(0.5, 0.5),
                    expand=True,
                )
            ],
        )

    def dashboard_view():
        card_1 = card_container(
            ft.Column(
                controls=[
                    ft.Text("Audi A4", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Precio: $15.000", color=ft.Colors.WHITE70),
                ],
                spacing=4,
            ),
            width=300,
        )

        card_2 = card_container(
            ft.Column(
                controls=[
                    ft.Text("BMW i3", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Precio: $18.500", color=ft.Colors.WHITE70),
                ],
                spacing=4,
            ),
            width=300,
        )

        cards = cast(list[ft.Control], [card_1, card_2])

        return ft.View(
            route="/dashboard",
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Row(controls=cards, wrap=True, spacing=12),
                    ],
                    spacing=20,
                    expand=True,
                )
            ],
        )

    def route_change(e):
        page.views.clear()
        if page.route == "/login":
            page.views.append(login_view())
        elif page.route == "/dashboard":
            page.views.append(dashboard_view())
        else:
            page.views.append(login_view())
        page.update()

    page.on_route_change = route_change
    page.go("/login")


if __name__ == "__main__":
    ft.run(main)