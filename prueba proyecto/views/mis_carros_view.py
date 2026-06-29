"""
Pestaña 'MIS CARROS'.

Muestra todo lo que el usuario logueado ha publicado (pendiente de revisión,
activo, vendido, no vendido o rechazado) y permite publicar un carro nuevo a
través de un formulario plegable con:
- Datos básicos y especificaciones técnicas.
- Información para que un admin/experto pueda verificar el vehículo
  (condición general, descripción de daños, documentos en regla).
- Una foto del vehículo, pegando un link de imagen.

Todo lo publicado nace en estado 'pendiente_revision' — ver views/revision_view.py.
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, estado_badge, empty_state, auto_imagen

CONDICIONES = ["Excelente", "Buena", "Regular", "Necesita reparación"]


def _fila_carro(c: dict) -> ft.Container:
    info_extra = ""
    if c["estado_subasta"] == "pendiente_revision":
        info_extra = "En revisión por nuestro equipo. Te avisaremos cuando se apruebe."
    elif c["estado_subasta"] == "rechazada":
        info_extra = f'Rechazada: {c["motivo_rechazo"]}'

    columna_izquierda = ft.Column(
        [
            ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                     size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
            ft.Text(f'{c["kilometraje"]:,} km · Base {money(c["precio_base"])} · '
                    f'Reserva {money(c["precio_reserva"])}',
                    size=12, color=Colors.TEXT_SECONDARY),
        ],
        spacing=2,
        expand=True,
    )
    if info_extra:
        columna_izquierda.controls.append(
            ft.Text(info_extra, size=12,
                     color="#E2B33E" if c["estado_subasta"] == "pendiente_revision" else "#E26A6A")
        )

    return card(
        ft.Row(
            [
                auto_imagen(c.get("imagen"), width=88, height=64),
                columna_izquierda,
                ft.Column(
                    [
                        ft.Text(f'{c["num_pujas"]} pujas · mejor: {money(c["puja_maxima"])}',
                                 size=12, color=Colors.TEXT_SECONDARY),
                        ft.Container(height=4),
                        estado_badge(c["estado_subasta"]),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=0,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=16,
        ),
        padding=16,
    )


def mis_carros_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None, on_profile_click=None) -> ft.Container:
    mis_carros = sistema.obtener_mis_carros(usuario_actual.id)

    # --- Campos del formulario (datos básicos) ---
    marca_f = ft.TextField(label="Marca", width=180)
    modelo_f = ft.TextField(label="Modelo", width=180)
    anio_f = ft.TextField(label="Año", width=100)
    km_f = ft.TextField(label="Kilometraje", width=140)
    base_f = ft.TextField(label="Precio base", width=160)
    reserva_f = ft.TextField(label="Precio reserva", width=160)
    dias_f = ft.TextField(label="Días de duración", width=160, value="7")

    # --- Especificaciones técnicas ---
    motor_f = ft.TextField(label="Motor", width=180)
    transmision_f = ft.TextField(label="Transmisión", width=180)
    combustible_f = ft.TextField(label="Combustible", width=180)
    color_f = ft.TextField(label="Color", width=180)
    extras_f = ft.TextField(label="Extras (separados por coma)", width=380)

    # --- Verificación para el admin/experto ---
    condicion_f = ft.Dropdown(
        label="Condición general",
        width=220,
        options=[ft.DropdownOption(text=c) for c in CONDICIONES],
        value=CONDICIONES[0],
    )
    danos_f = ft.TextField(
        label="Descripción de daños o desperfectos (si aplica)",
        width=380, multiline=True, min_lines=2, max_lines=4,
    )
    documentos_f = ft.Checkbox(label="Los documentos del vehículo están en regla", value=False)

    # --- Imagen: se pega un link (sin selector de archivos: ese control
    # no es estable entre versiones de Flet — ver el error reportado). ---
    imagen_url_f = ft.TextField(label="Link de imagen (opcional)", width=300)
    imagen_preview = ft.Container(content=auto_imagen(None, width=120, height=90))

    def handle_vista_previa(e):
        imagen_preview.content = auto_imagen((imagen_url_f.value or "").strip() or None, width=120, height=90)
        page.update()

    vista_previa_btn = ft.TextButton(
        content=ft.Text("Vista previa", color=Colors.ACCENT_INDIGO, size=12),
        on_click=handle_vista_previa,
    )

    error_text = ft.Text("", color="#E26A6A", size=12)
    estado_form = {"visible": False}
    form_container = ft.Container(visible=False)

    def construir_formulario():
        return card(
            ft.Column(
                [
                    ft.Text("Publicar un carro nuevo", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    ft.Container(height=12),
                    ft.Text("Datos básicos", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=6),
                    ft.Row([marca_f, modelo_f, anio_f], spacing=12),
                    ft.Container(height=8),
                    ft.Row([km_f, base_f, reserva_f, dias_f], spacing=12),

                    ft.Container(height=16),
                    ft.Text("Especificaciones técnicas", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=6),
                    ft.Row([motor_f, transmision_f, combustible_f, color_f], spacing=12),
                    ft.Container(height=8),
                    extras_f,

                    ft.Container(height=16),
                    ft.Text("Verificación del vehículo", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Text("Un experto de la plataforma revisa esto antes de publicar la subasta.",
                             size=11, color=Colors.TEXT_MUTED),
                    ft.Container(height=6),
                    ft.Row([condicion_f], spacing=12),
                    ft.Container(height=8),
                    danos_f,
                    ft.Container(height=8),
                    documentos_f,

                    ft.Container(height=16),
                    ft.Text("Foto del vehículo", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                    ft.Container(height=6),
                    ft.Row(
                        [
                            imagen_preview,
                            ft.Column([imagen_url_f, vista_previa_btn], spacing=4),
                        ],
                        spacing=16,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),

                    error_text,
                    ft.Container(height=12),
                    ft.ElevatedButton(
                        content=ft.Text("Enviar a revisión"),
                        bgcolor=Colors.BUTTON_BG,
                        color=Colors.BUTTON_TEXT,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=handle_publicar,
                    ),
                ],
                spacing=0,
            ),
            padding=20,
        )

    def handle_publicar(e):
        try:
            anio = int(anio_f.value)
            km = int(km_f.value)
            base = float(base_f.value)
            reserva = float(reserva_f.value)
            dias = int(dias_f.value)
        except (TypeError, ValueError):
            error_text.value = "Año, kilometraje, precios y días deben ser números."
            page.update()
            return

        if not marca_f.value or not modelo_f.value:
            error_text.value = "Marca y modelo son obligatorios."
            page.update()
            return

        especificaciones = {
            k: v for k, v in {
                "motor": motor_f.value, "transmision": transmision_f.value,
                "combustible": combustible_f.value, "color": color_f.value,
            }.items() if v
        }
        extras = [x.strip() for x in (extras_f.value or "").split(",") if x.strip()]
        imagen_final = (imagen_url_f.value or "").strip() or None

        ok, resultado = sistema.publicar_carro(
            id_vendedor=usuario_actual.id, marca=marca_f.value, modelo=modelo_f.value,
            anio=anio, kilometraje=km, precio_base=base, precio_reserva=reserva,
            dias_duracion=dias, especificaciones=especificaciones, extras=extras,
            imagen=imagen_final, condicion_general=condicion_f.value,
            descripcion_danos=danos_f.value or "", documentos_en_regla=documentos_f.value,
        )
        if not ok:
            error_text.value = resultado
            page.update()
            return

        if on_change:
            on_change()  # guarda en disco y reconstruye esta misma vista

    def toggle_formulario(e):
        estado_form["visible"] = not estado_form["visible"]
        form_container.content = construir_formulario() if estado_form["visible"] else None
        form_container.visible = estado_form["visible"]
        toggle_btn_text.value = "− Cancelar" if estado_form["visible"] else "+ Publicar un carro"
        page.update()

    toggle_btn_text = ft.Text("+ Publicar un carro")
    toggle_btn = ft.ElevatedButton(
        content=toggle_btn_text,
        bgcolor=Colors.BUTTON_BG,
        color=Colors.BUTTON_TEXT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=toggle_formulario,
    )

    lista = [_fila_carro(c) for c in mis_carros] if mis_carros else [
        empty_state("Todavía no has publicado ningún carro.")
    ]

    body = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Mis Carros", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    toggle_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=Sizes.GAP),
            form_container,
            ft.Container(height=Sizes.GAP if estado_form["visible"] else 0),
            *[item for c in lista for item in (c, ft.Container(height=12))],
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "MIS CARROS", body, on_nav_click=on_nav_click, on_profile_click=on_profile_click)
