import flet as ft
from pathlib import Path

from admin.admin import AdministradorCompraVenta

BASE_DIR = Path(__file__).resolve().parent


class AppState:
    def __init__(self) -> None:
        self.admin_backend = AdministradorCompraVenta()
        self.usuario_activo = None


state = AppState()


def cargar_base_datos_real() -> None:
    try:
        with (BASE_DIR / "usuarios.json").open("r", encoding="utf-8") as f:
            js_usuarios = f.read()
        with (BASE_DIR / "carros.json").open("r", encoding="utf-8") as f:
            js_carros = f.read()
        with (BASE_DIR / "subastas.json").open("r", encoding="utf-8") as f:
            js_pujas = f.read()

        state.admin_backend.cargar_datos_desde_json(js_usuarios, js_carros, js_pujas)
    except Exception as e:
        print(f"Error al cargar archivos JSON locales: {e}")


cargar_base_datos_real()


def main(page: ft.Page):
    page.title = "Sistema de Subastas de Carros"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 1200
    page.window.height = 850

    BG_COLOR = "#0e111d"
    CARD_COLOR = "#1a1c30"
    TEXT_MAIN = "#ffffff"
    TEXT_MUTED = "#ffffffb3"
    ACCENT_COLOR = "#3b82f6"

    email_field = ft.TextField(
        hint_text="Ingresa tu correo (ej: ana.lepage@email.com)",
        width=400,
        bgcolor="#ffffff",
        color="#111111",
        border_radius=8,
    )
    error_message = ft.Text("", color="#ef4444", size=13)

    def validar_y_loguear(e):
        del e
        correo_ingresado = email_field.value.strip() if email_field.value else ""

        if not correo_ingresado:
            error_message.value = "Por favor, escribe un correo electrónico."
            page.update()
            return

        user_encontrado = None
        for usr_obj in state.admin_backend.usuarios.values():
            if usr_obj.email.lower() == correo_ingresado.lower():
                user_encontrado = usr_obj
                break

        if user_encontrado:
            state.usuario_activo = user_encontrado
            error_message.value = ""
            show_dashboard()
        else:
            error_message.value = "El correo no está registrado en el sistema."
            page.update()

    def login_view():
        login_column = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("subasta", size=60, weight=ft.FontWeight.W_300, color=TEXT_MAIN),
                ft.Container(height=10),
                ft.Text("Acceso al Sistema de Control", size=20, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Text("Conectado a la base de datos JSON", color=TEXT_MUTED),
                ft.Container(height=20),
                email_field,
                error_message,
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Iniciar Sesión Auténtica",
                    width=400,
                    style=ft.ButtonStyle(
                        bgcolor=ACCENT_COLOR,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=validar_y_loguear,
                ),
                ft.Container(height=20),
                ft.Text("Prueba con: ana.lepage@email.com o carlos.m@email.com", color=ft.Colors.WHITE54, size=11),
            ],
        )

        return ft.View(
            route="/login",
            bgcolor=BG_COLOR,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[login_column],
        )

    def card_container(content, expand: bool | int = False, height=None):
        return ft.Container(
            content=content,
            bgcolor=CARD_COLOR,
            border_radius=10,
            padding=20,
            height=height,
            expand=expand,
        )

    def dashboard_view():
        if state.usuario_activo is None:
            return login_view()

        total_ganancias = sum(
            c.precio_final_venta for c in state.admin_backend.carros.values() if c.estado_subasta == "vendido"
        )
        activas_totales = sum(1 for c in state.admin_backend.carros.values() if c.estado_subasta == "activa")

        total_pujado_usuario = 0
        for puja in state.admin_backend.pujas:
            if puja.id_usuario == state.usuario_activo.id:
                total_pujado_usuario += puja.monto

        nav_bar = ft.Container(
            padding=20,
            bgcolor=BG_COLOR,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("DASHBOARD SUBASTAS", size=18, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Row(
                        spacing=20,
                        controls=[
                            ft.Text("RESUMEN", color=ACCENT_COLOR, weight=ft.FontWeight.BOLD),
                            ft.Text(f"ROL: {state.usuario_activo.rol.upper()}", color=TEXT_MUTED, size=12),
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(f"Hola, {state.usuario_activo.nombre}", color=TEXT_MAIN, weight=ft.FontWeight.W_500),
                            ft.CircleAvatar(bgcolor=ft.Colors.BLUE_GREY_700, content=ft.Text(state.usuario_activo.nombre[0])),
                        ]
                    ),
                ],
            ),
        )

        summary_cards = ft.Row(
            spacing=20,
            controls=[
                card_container(
                    ft.Column([
                        ft.Text("GANANCIAS DEL SISTEMA", size=11, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
                        ft.Text(f"${total_ganancias:,.2f}", size=28, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Text("Suma de autos vendidos", size=11, color="#22c55e"),
                    ]),
                    expand=True,
                ),
                card_container(
                    ft.Column([
                        ft.Text("MIS OFERTAS ACUMULADAS", size=11, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
                        ft.Text(f"${total_pujado_usuario:,.2f}", size=28, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Text("Tu capital en juego", size=11, color=ACCENT_COLOR),
                    ]),
                    expand=True,
                ),
                card_container(
                    ft.Column([
                        ft.Text("SUBASTAS ACTIVAS", size=11, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
                        ft.Text(str(activas_totales), size=28, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Text("Vehículos disponibles hoy", size=11, color=TEXT_MUTED),
                    ]),
                    expand=True,
                ),
            ],
        )

        lista_usuarios_widgets = []
        for _, u in state.admin_backend.usuarios.items():
            lista_usuarios_widgets.append(
                ft.ListTile(
                    leading=ft.CircleAvatar(bgcolor=ft.Colors.BLUE_800, content=ft.Text(u.nombre[0])),
                    title=ft.Text(u.nombre, size=14, color=TEXT_MAIN, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"{u.email} • Rep: {u.reputacion}⭐", size=12, color=TEXT_MUTED),
                    trailing=ft.Container(
                        content=ft.Text(u.rol.upper(), size=10, color="#111111", weight=ft.FontWeight.BOLD),
                        bgcolor="#00bcd4" if u.rol == "vendedor" else "#ffb300",
                        padding=5,
                        border_radius=5,
                    ),
                )
            )

        middle_section = ft.Row(
            spacing=20,
            controls=[
                card_container(
                    ft.Column([
                        ft.Text("ESTADO DEL INVENTARIO (JSON)", size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Container(height=10),
                        ft.Text(f"Total de Vehículos registrados: {len(state.admin_backend.carros)}", color=TEXT_MUTED),
                        ft.Divider(color="#2a2d45"),
                        ft.ListView(
                            expand=True,
                            controls=[
                                ft.Text(
                                    f"• [{c.id}] {c.marca} {c.modelo} ({c.anio}) - Estado: {c.estado_subasta}",
                                    size=13,
                                    color=TEXT_MAIN,
                                )
                                for c in state.admin_backend.carros.values()
                            ],
                        ),
                    ]),
                    expand=2,
                    height=350,
                ),
                card_container(
                    ft.Column([
                        ft.Text("USUARIOS EN EL SISTEMA", size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Container(height=5),
                        ft.ListView(expand=True, spacing=5, controls=lista_usuarios_widgets),
                    ]),
                    expand=1,
                    height=350,
                ),
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
                        controls=[summary_cards, middle_section],
                    ),
                ),
            ],
        )

    def show_login():
        page.views.clear()
        page.views.append(login_view())
        page.update()

    def show_dashboard():
        page.views.clear()
        page.views.append(dashboard_view())
        page.update()

    def route_change(_e):
        del _e
        if page.route == "/dashboard":
            if state.usuario_activo is None:
                show_login()
            else:
                show_dashboard()
        else:
            show_login()

    page.on_route_change = route_change
    show_login()


if __name__ == "__main__":
    ft.run(main)