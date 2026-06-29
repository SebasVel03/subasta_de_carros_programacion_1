"""
Vista de Login / Registro, conectada al backend real.

Mantiene el lenguaje visual de la referencia ("subasta" + formulario simple),
pero con dos diferencias necesarias para que funcione con el backend:

1. Se agregó un campo de "Nombre completo" (solo visible en modo registro):
   el backend necesita un nombre para crear el Usuario.
2. Se agregó un campo de "Contraseña": el mockup original solo pedía el
   correo, pero autenticar_usuario() del backend SÍ valida contraseña.
   Si el equipo quiere un registro 100% sin contraseña (passwordless /
   "magic link"), es una decisión de producto a tomar aparte — eso no
   está implementado todavía.

La misma vista sirve para "Crear cuenta" e "Iniciar sesión"; el link
"inicia sesion" / "regístrate" alterna entre los dos modos sin recargar
toda la pantalla.
"""

import flet as ft
from theme import Colors


def login_view(page: ft.Page, sistema, on_login_success=None) -> ft.Container:
    """
    sistema: instancia de backend.AdministradorCompraVenta ya cargada con datos.
    on_login_success(usuario): se llama cuando el login o el registro funcionó.
    """

    estado = {"modo": "registro"}  # "registro" | "login"

    nombre_field = ft.TextField(
        hint_text="Nombre completo",
        hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
        bgcolor=Colors.INPUT_BG,
        color=Colors.INPUT_TEXT,
        border_color="transparent",
        focused_border_color=Colors.ACCENT_INDIGO,
        border_radius=8,
        width=380,
        height=48,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        text_size=14,
    )

    email_field = ft.TextField(
        hint_text="correoelectrónico@dominio.com",
        hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
        bgcolor=Colors.INPUT_BG,
        color=Colors.INPUT_TEXT,
        border_color="transparent",
        focused_border_color=Colors.ACCENT_INDIGO,
        border_radius=8,
        width=380,
        height=48,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        text_size=14,
    )

    password_field = ft.TextField(
        hint_text="Contraseña",
        hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
        password=True,
        can_reveal_password=True,
        bgcolor=Colors.INPUT_BG,
        color=Colors.INPUT_TEXT,
        border_color="transparent",
        focused_border_color=Colors.ACCENT_INDIGO,
        border_radius=8,
        width=380,
        height=48,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        text_size=14,
    )

    rol_field = ft.RadioGroup(
        value="usuario",
        content=ft.Column(
            [
                ft.Radio(value="usuario", label="Quiero comprar y vender autos",
                         label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=13)),
                # NOTA PARA EL EQUIPO: dejar que cualquiera intente registrarse
                # como 'admin' desde este formulario es solo un atajo de demo
                # para poder probar la pantalla de Revisión sin montar un
                # proceso de invitación aparte (por eso pide un código). En
                # producción, las cuentas de admin/experto NO deberían poder
                # crearse desde un registro público en absoluto.
                ft.Radio(value="admin", label="Soy experto/administrador (revisión de vehículos)",
                         label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=13)),
            ],
            spacing=4,
        ),
        on_change=lambda e: (sincronizar_ui(), page.update()),
    )

    codigo_admin_field = ft.TextField(
        hint_text="Código de administrador",
        hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
        bgcolor=Colors.INPUT_BG,
        color=Colors.INPUT_TEXT,
        border_color="transparent",
        focused_border_color=Colors.ACCENT_INDIGO,
        border_radius=8,
        width=380,
        height=48,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        text_size=14,
        visible=False,
    )

    error_text = ft.Text("", color=ft.Colors.RED_300, size=12)
    titulo_text = ft.Text("Crea una cuenta", size=20, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY)
    subtitulo_text = ft.Text(
        "Ingresa tus datos para registrarte en esta app",
        size=14,
        color=Colors.TEXT_SECONDARY,
    )
    submit_button_text = ft.Text("Registrarse con correo electrónico", size=14, weight=ft.FontWeight.W_500)
    toggle_prefix_text = ft.Text("si ya tienes cuenta, ", color=Colors.TEXT_SECONDARY, size=13)
    toggle_link_text = ft.Text("inicia sesion", color=Colors.ACCENT_INDIGO, size=13)

    def sincronizar_ui():
        es_registro = estado["modo"] == "registro"
        nombre_field.visible = es_registro
        rol_field.visible = es_registro
        codigo_admin_field.visible = es_registro and rol_field.value == "admin"
        titulo_text.value = "Crea una cuenta" if es_registro else "Inicia sesión"
        subtitulo_text.value = (
            "Ingresa tus datos para registrarte en esta app" if es_registro
            else "Ingresa tu correo y contraseña para continuar"
        )
        submit_button_text.value = (
            "Registrarse con correo electrónico" if es_registro else "Iniciar sesión"
        )
        toggle_prefix_text.value = "si ya tienes cuenta, " if es_registro else "si no tienes cuenta, "
        toggle_link_text.value = "inicia sesion" if es_registro else "regístrate"
        error_text.value = ""

    def alternar_modo(e):
        estado["modo"] = "login" if estado["modo"] == "registro" else "registro"
        sincronizar_ui()
        page.update()

    def handle_submit(e):
        email = (email_field.value or "").strip()
        password = password_field.value or ""

        if "@" not in email or "." not in email:
            error_text.value = "Ingresa un correo electrónico válido."
            page.update()
            return
        if len(password) < 6:
            error_text.value = "La contraseña debe tener al menos 6 caracteres."
            page.update()
            return

        if estado["modo"] == "registro":
            nombre = (nombre_field.value or "").strip()
            if not nombre:
                error_text.value = "Ingresa tu nombre completo."
                page.update()
                return
            # El usuario elige si quiere participar como usuario normal
            # (puede comprar y vender) o pedir acceso de admin/experto.
            ok, resultado = sistema.registrar_usuario(
                nombre, email, password, rol=rol_field.value,
                codigo_admin=codigo_admin_field.value if rol_field.value == "admin" else None,
            )
        else:
            ok, resultado = sistema.autenticar_usuario(email, password)

        if not ok:
            error_text.value = resultado  # resultado es el mensaje de error
            page.update()
            return

        error_text.value = ""
        page.update()
        if on_login_success:
            on_login_success(resultado)  # resultado es el objeto Usuario

    submit_button = ft.ElevatedButton(
        content=submit_button_text,
        width=380,
        height=48,
        bgcolor=Colors.BUTTON_BG,
        color=Colors.BUTTON_TEXT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), elevation=0),
        on_click=handle_submit,
    )

    toggle_row = ft.Row(
        [
            toggle_prefix_text,
            ft.TextButton(
                content=toggle_link_text,
                style=ft.ButtonStyle(padding=0),
                on_click=alternar_modo,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0,
        tight=True,
    )

    terms_text = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Al hacer clic en Continuar aceptas nuestros ", color=Colors.TEXT_MUTED, size=12),
                    ft.TextButton(
                        content=ft.Text("Términos de servicio", color=Colors.ACCENT_INDIGO, size=12),
                        style=ft.ButtonStyle(padding=0),
                    ),
                    ft.Text(" y la", color=Colors.TEXT_MUTED, size=12),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0,
                tight=True,
            ),
            ft.TextButton(
                content=ft.Text("Política de privacidad", color=Colors.ACCENT_INDIGO, size=12),
                style=ft.ButtonStyle(padding=0),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    sincronizar_ui()  # estado inicial coherente

    content = ft.Column(
        [
            ft.Container(height=24),
            ft.Text("subasta", size=64, weight=ft.FontWeight.W_300, color=Colors.TEXT_PRIMARY, font_family="Courier New"),
            ft.Container(height=20),
            titulo_text,
            subtitulo_text,
            ft.Container(height=16),
            nombre_field,
            ft.Container(height=10),
            email_field,
            ft.Container(height=10),
            password_field,
            ft.Container(height=6),
            rol_field,
            codigo_admin_field,
            error_text,
            ft.Container(height=4),
            submit_button,
            toggle_row,
            ft.Container(height=20),
            terms_text,
            ft.Container(height=20),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=content,
        bgcolor=Colors.BACKGROUND,
        expand=True,
        alignment=ft.Alignment.TOP_CENTER,
        padding=ft.Padding.only(top=12, bottom=12),
    )
