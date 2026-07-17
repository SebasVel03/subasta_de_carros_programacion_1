"""
Pantalla de Perfil (se abre al hacer clic en el nombre/avatar de la barra
superior, no es una pestaña más del menú). Incluye:

- Información básica de la cuenta activa.
- Foto de perfil: pegar un link o subir un archivo del dispositivo (mismo
  mecanismo que la foto de un carro en Mis Carros — ver ese archivo).
- Configuración simple: editar nombre/teléfono, cambiar contraseña.
- Apariencia: modo claro/oscuro (ver theme.py: Colors.aplicar_modo). El
  cambio es INMEDIATO y global — no hace falta guardar aparte, ya que
  on_toggle_tema (implementado en main.py) persiste la preferencia a disco
  y reconstruye la pantalla apenas se mueve el switch.
- Selector de cuentas: si la persona inició sesión con más de una cuenta en
  esta misma sesión de la app, puede cambiar entre ellas sin volver a
  escribir la contraseña, agregar otra cuenta, o cerrar sesión.
"""

import base64

import flet as ft
from theme import Colors, Sizes, card
from views.shared import (
    page_shell, empty_state, avatar_imagen,
    TAMANO_MAXIMO_IMAGEN_MB, TAMANO_MAXIMO_IMAGEN_BYTES,
)


def _fila_cuenta(usuario, es_actual, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                avatar_imagen(usuario.foto_perfil, size=36,
                              bgcolor_respaldo=Colors.ACCENT_INDIGO if es_actual else None),
                ft.Column(
                    [
                        ft.Text(usuario.nombre, size=13, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                        ft.Text(usuario.email, size=11, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=Colors.ACCENT_TEAL, size=18) if es_actual else ft.Container(),
            ],
            spacing=10,
        ),
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        border_radius=8,
        bgcolor=Colors.SURFACE_ALT if es_actual else None,
        on_click=None if es_actual else (lambda e: on_click(usuario)),
    )


def perfil_view(page: ft.Page, sistema, usuario_actual, cuentas_sesion=None,
                 on_nav_click=None, on_change=None, on_account_click=None, on_search=None, valor_busqueda="",
                 on_switch_account=None, on_add_account=None, on_logout=None,
                 on_messages_click=None, on_toggle_tema=None, modo_claro=False) -> ft.Container:
    cuentas_sesion = cuentas_sesion or ([usuario_actual] if usuario_actual else [])

    # --- Tarjeta de información básica ---
    info_card = card(
        ft.Column(
            [
                ft.Row(
                    [
                        avatar_imagen(usuario_actual.foto_perfil, size=64),
                        ft.Column(
                            [
                                ft.Text(usuario_actual.nombre, size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                ft.Text(usuario_actual.email, size=13, color=Colors.TEXT_SECONDARY),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=16,
                ),
                ft.Container(height=16),
                ft.Divider(color=Colors.BORDER, height=1),
                ft.Container(height=16),
                ft.Row(
                    [
                        ft.Column([ft.Text("ROL", size=11, color=Colors.TEXT_SECONDARY),
                                    ft.Text(usuario_actual.rol.capitalize(), size=14, color=Colors.TEXT_PRIMARY)], spacing=2),
                        ft.Column([ft.Text("VERIFICADO", size=11, color=Colors.TEXT_SECONDARY),
                                    ft.Text("Sí" if usuario_actual.verificado else "No", size=14, color=Colors.TEXT_PRIMARY)], spacing=2),
                        ft.Column([ft.Text("REPUTACIÓN", size=11, color=Colors.TEXT_SECONDARY),
                                    ft.Text(f"{usuario_actual.reputacion} ⭐", size=14, color=Colors.TEXT_PRIMARY)], spacing=2),
                        ft.Column([ft.Text("MIEMBRO DESDE", size=11, color=Colors.TEXT_SECONDARY),
                                    ft.Text((usuario_actual.fecha_registro or "")[:10], size=14, color=Colors.TEXT_PRIMARY)], spacing=2),
                    ],
                    spacing=28,
                ),
            ],
            spacing=0,
        ),
        padding=20,
    )

    # --- Configuración: foto de perfil. Mismo mecanismo que la foto de un
    # carro en Mis Carros: pegar un link o subir un archivo del dispositivo,
    # ambos caminos terminan fijando imagen_estado["valor"] (patrón
    # {"valor": ...} en vez de nonlocal) con una URL o un string base64. ---
    TAMANO_PREVIEW_FOTO = 96
    imagen_estado = {"valor": usuario_actual.foto_perfil}

    foto_preview = ft.Container(content=avatar_imagen(imagen_estado["valor"], size=TAMANO_PREVIEW_FOTO))
    foto_url_f = ft.TextField(label="Link de imagen (opcional)", width=300)
    foto_info = ft.Text("", size=11, color=Colors.TEXT_MUTED)
    foto_feedback = ft.Text("", size=12)

    def handle_vista_previa_foto(e):
        url = (foto_url_f.value or "").strip() or None
        imagen_estado["valor"] = url
        foto_info.value = "Se usará el link de arriba." if url else ""
        foto_info.color = Colors.TEXT_MUTED
        foto_preview.content = avatar_imagen(url, size=TAMANO_PREVIEW_FOTO)
        page.update()

    vista_previa_foto_btn = ft.TextButton(
        content=ft.Text("Vista previa", color=Colors.ACCENT_INDIGO, size=12),
        on_click=handle_vista_previa_foto,
    )

    # NOTA DE COMPATIBILIDAD (Flet 0.85.3): igual que en mis_carros_view.py,
    # ft.FilePicker se autorregistra por contexto y no necesita agregarse a
    # page.overlay; pick_files() es async y devuelve directamente la lista
    # de archivos.
    foto_file_picker = ft.FilePicker()

    async def handle_subir_foto(e):
        archivos = await foto_file_picker.pick_files(
            dialog_title="Selecciona tu foto de perfil",
            file_type=ft.FilePickerFileType.IMAGE,
            allow_multiple=False,
            with_data=True,
        )
        if not archivos:
            return  # el usuario cerró el selector sin elegir nada

        archivo = archivos[0]
        if not archivo.bytes:
            foto_info.value = "No se pudo leer el archivo seleccionado."
            foto_info.color = "#E26A6A"
            page.update()
            return
        if len(archivo.bytes) > TAMANO_MAXIMO_IMAGEN_BYTES:
            foto_info.value = f"La imagen pesa demasiado (máximo {TAMANO_MAXIMO_IMAGEN_MB} MB)."
            foto_info.color = "#E26A6A"
            page.update()
            return

        foto_b64 = base64.b64encode(archivo.bytes).decode("ascii")
        imagen_estado["valor"] = foto_b64
        foto_url_f.value = ""  # el archivo subido tiene prioridad sobre el link
        foto_info.value = f"Imagen cargada desde el dispositivo: {archivo.name}"
        foto_info.color = Colors.ACCENT_TEAL
        foto_preview.content = avatar_imagen(foto_b64, size=TAMANO_PREVIEW_FOTO)
        page.update()

    subir_foto_btn = ft.OutlinedButton(
        content=ft.Text("Subir desde el dispositivo", size=12),
        on_click=handle_subir_foto,
    )

    def handle_guardar_foto(e):
        ok, resultado = sistema.actualizar_foto_perfil(usuario_actual.id, imagen_estado["valor"])
        if not ok:
            foto_feedback.value = resultado
            foto_feedback.color = "#E26A6A"
            page.update()
            return
        foto_feedback.value = "Foto de perfil actualizada."
        foto_feedback.color = Colors.ACCENT_TEAL
        if on_change:
            on_change()
        else:
            page.update()

    def handle_quitar_foto(e):
        ok, resultado = sistema.actualizar_foto_perfil(usuario_actual.id, None)
        if not ok:
            foto_feedback.value = resultado
            foto_feedback.color = "#E26A6A"
            page.update()
            return
        imagen_estado["valor"] = None
        foto_url_f.value = ""
        foto_info.value = ""
        foto_feedback.value = "Foto de perfil eliminada."
        foto_feedback.color = Colors.ACCENT_TEAL
        if on_change:
            on_change()
        else:
            page.update()

    foto_perfil_card = card(
        ft.Column(
            [
                ft.Text("Foto de perfil", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Text("Pega un link o sube una foto desde tu dispositivo.",
                         size=11, color=Colors.TEXT_MUTED),
                ft.Container(height=12),
                ft.Row(
                    [
                        foto_preview,
                        ft.Column(
                            [
                                foto_url_f,
                                ft.Row([vista_previa_foto_btn, subir_foto_btn], spacing=8, wrap=True),
                                foto_info,
                            ],
                            spacing=6,
                        ),
                    ],
                    spacing=16,
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                foto_feedback,
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            content=ft.Text("Guardar foto"),
                            bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=handle_guardar_foto,
                        ),
                        ft.OutlinedButton(
                            content=ft.Text("Quitar foto"),
                            on_click=handle_quitar_foto,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            spacing=0,
        ),
        padding=20,
    )

    # --- Configuración: editar datos básicos ---
    nombre_f = ft.TextField(label="Nombre completo", value=usuario_actual.nombre, width=300)
    telefono_f = ft.TextField(label="Teléfono", value=usuario_actual.telefono or "", width=300)
    datos_feedback = ft.Text("", size=12)

    def handle_guardar_datos(e):
        ok, resultado = sistema.actualizar_perfil(usuario_actual.id, nombre=nombre_f.value, telefono=telefono_f.value)
        if not ok:
            datos_feedback.value = resultado
            datos_feedback.color = "#E26A6A"
            page.update()
            return
        datos_feedback.value = "Datos actualizados."
        datos_feedback.color = Colors.ACCENT_TEAL
        if on_change:
            on_change()
        else:
            page.update()

    datos_card = card(
        ft.Column(
            [
                ft.Text("Información básica", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Container(height=12),
                ft.Row([nombre_f, telefono_f], spacing=12),
                datos_feedback,
                ft.Container(height=8),
                ft.ElevatedButton(
                    content=ft.Text("Guardar cambios"),
                    bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=handle_guardar_datos,
                ),
            ],
            spacing=0,
        ),
        padding=20,
        expand=True,
    )

    # --- Configuración: cambiar contraseña ---
    actual_f = ft.TextField(label="Contraseña actual", password=True, can_reveal_password=True, width=300)
    nueva_f = ft.TextField(label="Contraseña nueva", password=True, can_reveal_password=True, width=300)
    password_feedback = ft.Text("", size=12)

    def handle_cambiar_password(e):
        ok, resultado = sistema.cambiar_password(usuario_actual.id, actual_f.value or "", nueva_f.value or "")
        if not ok:
            password_feedback.value = resultado
            password_feedback.color = "#E26A6A"
            page.update()
            return
        actual_f.value = ""
        nueva_f.value = ""
        password_feedback.value = "Contraseña actualizada."
        password_feedback.color = Colors.ACCENT_TEAL
        if on_change:
            on_change()
        else:
            page.update()

    password_card = card(
        ft.Column(
            [
                ft.Text("Cambiar contraseña", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Container(height=12),
                ft.Row([actual_f, nueva_f], spacing=12),
                password_feedback,
                ft.Container(height=8),
                ft.ElevatedButton(
                    content=ft.Text("Actualizar contraseña"),
                    bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=handle_cambiar_password,
                ),
            ],
            spacing=0,
        ),
        padding=20,
        expand=True,
    )

    # --- Apariencia: modo claro / oscuro (ver theme.py: Colors.aplicar_modo).
    # El switch no tiene botón de "guardar" propio a propósito: on_toggle_tema
    # (implementado en main.py) ya persiste la preferencia y reconstruye la
    # pantalla apenas cambia, así que el efecto es inmediato — igual que
    # cambiar de pestaña, no hace falta una confirmación extra acá. ---
    def handle_cambio_tema(e):
        if on_toggle_tema:
            on_toggle_tema(e.control.value)
        # No hace falta page.update(): on_toggle_tema reconstruye toda la
        # pantalla (refrescar_vista_actual), incluido este switch con el
        # nuevo valor ya reflejado.

    apariencia_card = card(
        ft.Column(
            [
                ft.Text("Apariencia", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Container(height=12),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Modo claro", size=13, color=Colors.TEXT_PRIMARY),
                                ft.Text("Cambia el fondo oscuro de la app por uno claro.",
                                         size=11, color=Colors.TEXT_MUTED),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Switch(
                            value=modo_claro,
                            active_color=Colors.ACCENT_TEAL,
                            on_change=handle_cambio_tema,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=0,
        ),
        padding=20,
    )

    # --- Selector de cuentas ---
    filas_cuentas = [
        _fila_cuenta(u, u.id == usuario_actual.id, on_switch_account)
        for u in cuentas_sesion
    ]

    cuentas_card = card(
        ft.Column(
            [
                ft.Text("Cuentas en esta sesión", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Text("Cambia entre cuentas sin volver a escribir la contraseña.",
                         size=11, color=Colors.TEXT_MUTED),
                ft.Container(height=12),
                *filas_cuentas,
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.TextButton(
                            content=ft.Text("+ Agregar otra cuenta", color=Colors.ACCENT_INDIGO, size=13),
                            on_click=(lambda e: on_add_account()) if on_add_account else None,
                        ),
                        ft.TextButton(
                            content=ft.Text("Cerrar sesión", color="#E26A6A", size=13),
                            on_click=(lambda e: on_logout()) if on_logout else None,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=4,
        ),
        padding=20,
    )

    body = ft.Column(
        [
            ft.Text("Perfil", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Container(height=Sizes.GAP),
            info_card,
            ft.Container(height=Sizes.GAP),
            foto_perfil_card,
            ft.Container(height=Sizes.GAP),
            ft.Row([datos_card, password_card], spacing=Sizes.GAP, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Container(height=Sizes.GAP),
            apariencia_card,
            ft.Container(height=Sizes.GAP),
            cuentas_card,
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "PERFIL", body, sistema=sistema, on_nav_click=on_nav_click,
                       on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda,
                       on_messages_click=on_messages_click)
