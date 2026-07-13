"""
Pestaña 'MIS CARROS'.

Muestra todo lo que el usuario logueado ha publicado (pendiente de revisión,
activo, vendido, no vendido o rechazado) y permite publicar un carro nuevo a
través de un formulario plegable con:
- Datos básicos y especificaciones técnicas.
- Información para que un admin/experto pueda verificar el vehículo
  (condición general, descripción de daños, documentos en regla).
- Una foto del vehículo, ya sea pegando un link o subiendo un archivo del
  dispositivo (ver ft.FilePicker más abajo).

Todo lo publicado nace en estado 'pendiente_revision' — ver views/revision_view.py.

Debajo se agrega el subapartado 'Carros Ganados': subastas que este usuario
ganó como COMPRADOR y cuya entrega ya confirmó (ver
sistema.obtener_mis_carros_ganados / sistema.confirmar_entrega). Mientras
la entrega sigue pendiente, ese carro se ve únicamente en 'SUBASTAS
ACTIVAS' → 'Compras ganadas' (views/subastas_activas_view.py); en cuanto
se confirma, pasa a listarse acá — Mis Carros termina representando todo
lo que el usuario posee en este momento, ya sea porque lo publicó como
vendedor o porque lo ganó y ya lo recibió.
"""

import base64

import flet as ft
from theme import Colors, Sizes, card
from views.shared import (
    page_shell, money, estado_badge, empty_state, auto_imagen,
    TAMANO_MAXIMO_IMAGEN_MB, TAMANO_MAXIMO_IMAGEN_BYTES,
)
from views.detalle_subasta_dialog import mostrar_detalle_subasta

CONDICIONES = ["Excelente", "Buena", "Regular", "Necesita reparación"]


def _fila_carro(c: dict, sistema, usuario_actual, page, on_change) -> ft.Container:
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
        on_click=lambda e: mostrar_detalle_subasta(page, sistema, usuario_actual, c, on_change),
    )


def _fila_carro_ganado(c: dict, sistema, usuario_actual, page, on_change) -> ft.Container:
    """
    Fila del subapartado 'Carros Ganados': una subasta que este usuario
    ganó como comprador Y cuya entrega ya confirmó (ver
    sistema.obtener_mis_carros_ganados). Mientras la entrega todavía no se
    confirma, el mismo carro se sigue viendo únicamente en 'SUBASTAS
    ACTIVAS' → 'Compras ganadas'; acá es de solo lectura (no hay botón de
    confirmar entrega, porque para llegar a esta lista ya se confirmó).
    """
    fecha_entrega = (c.get("fecha_entrega_confirmada") or "")[:10]

    return card(
        ft.Row(
            [
                auto_imagen(c.get("imagen"), width=88, height=64),
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
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Text("✓ ENTREGADO", size=11, weight=ft.FontWeight.W_600, color=Colors.BACKGROUND),
                            bgcolor="#7ED957",
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                            border_radius=6,
                        ),
                        ft.Text(f'Recibido el {fecha_entrega}' if fecha_entrega else "",
                                 size=11, color=Colors.TEXT_MUTED),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=4,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=16,
        ),
        padding=16,
        on_click=lambda e: mostrar_detalle_subasta(page, sistema, usuario_actual, c, on_change),
    )


def mis_carros_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None,
                     on_account_click=None, on_search=None, valor_busqueda="", on_messages_click=None) -> ft.Container:
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

    # --- Imagen: se puede pegar un link o subir un archivo del dispositivo.
    # Cualquiera de las dos vías termina fijando imagen_estado["valor"]
    # (patrón {"valor": ...} en vez de nonlocal), que es lo que se manda a
    # publicar_carro() al final. El archivo subido se guarda como string
    # base64 (auto_imagen ya sabe mostrar tanto URLs como base64).
    #
    # NOTA DE COMPATIBILIDAD (Flet 0.85.3): en esta versión ft.FilePicker
    # se autorregistra por contexto y NO necesita agregarse a page.overlay;
    # además, pick_files() es async y devuelve directamente la lista de
    # archivos (no llega por un evento on_result separado como en versiones
    # más viejas de la documentación).
    imagen_estado = {"valor": None}
    ANCHO_PREVIEW, ALTO_PREVIEW = 340, 220

    imagen_url_f = ft.TextField(label="Link de imagen (opcional)", width=300)
    imagen_preview = ft.Container(content=auto_imagen(None, width=ANCHO_PREVIEW, height=ALTO_PREVIEW))
    imagen_info = ft.Text("", size=11, color=Colors.TEXT_MUTED)

    def handle_vista_previa(e):
        url = (imagen_url_f.value or "").strip() or None
        imagen_estado["valor"] = url
        imagen_info.value = "Se usará el link de arriba." if url else ""
        imagen_info.color = Colors.TEXT_MUTED
        imagen_preview.content = auto_imagen(url, width=ANCHO_PREVIEW, height=ALTO_PREVIEW)
        page.update()

    vista_previa_btn = ft.TextButton(
        content=ft.Text("Vista previa", color=Colors.ACCENT_INDIGO, size=12),
        on_click=handle_vista_previa,
    )

    file_picker = ft.FilePicker()

    async def handle_subir_archivo(e):
        archivos = await file_picker.pick_files(
            dialog_title="Selecciona una foto del vehículo",
            file_type=ft.FilePickerFileType.IMAGE,
            allow_multiple=False,
            with_data=True,
        )
        if not archivos:
            return  # el usuario cerró el selector sin elegir nada

        archivo = archivos[0]
        if not archivo.bytes:
            imagen_info.value = "No se pudo leer el archivo seleccionado."
            imagen_info.color = "#E26A6A"
            page.update()
            return
        if len(archivo.bytes) > TAMANO_MAXIMO_IMAGEN_BYTES:
            imagen_info.value = f"La imagen pesa demasiado (máximo {TAMANO_MAXIMO_IMAGEN_MB} MB)."
            imagen_info.color = "#E26A6A"
            page.update()
            return

        imagen_b64 = base64.b64encode(archivo.bytes).decode("ascii")
        imagen_estado["valor"] = imagen_b64
        imagen_url_f.value = ""  # el archivo subido tiene prioridad sobre el link
        imagen_info.value = f"Imagen cargada desde el dispositivo: {archivo.name}"
        imagen_info.color = Colors.ACCENT_TEAL
        imagen_preview.content = auto_imagen(imagen_b64, width=ANCHO_PREVIEW, height=ALTO_PREVIEW)
        page.update()

    subir_archivo_btn = ft.OutlinedButton(
        content=ft.Text("Subir desde el dispositivo", size=12),
        on_click=handle_subir_archivo,
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
                    ft.Text("Pega un link o sube una foto desde tu dispositivo.",
                             size=11, color=Colors.TEXT_MUTED),
                    ft.Container(height=6),
                    ft.Row(
                        [
                            imagen_preview,
                            ft.Column(
                                [
                                    imagen_url_f,
                                    ft.Row([vista_previa_btn, subir_archivo_btn], spacing=8, wrap=True),
                                    imagen_info,
                                ],
                                spacing=6,
                            ),
                        ],
                        spacing=16,
                        wrap=True,
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
        # Prioridad: lo último fijado explícitamente (link con "Vista previa" o
        # archivo subido) y, si nada de eso pasó, el texto que haya en el campo
        # de link aunque no se haya clickeado "Vista previa" (compatibilidad
        # con el flujo anterior de pegar-y-publicar directo).
        imagen_final = imagen_estado["valor"] or (imagen_url_f.value or "").strip() or None

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

    lista = [_fila_carro(c, sistema, usuario_actual, page, on_change) for c in mis_carros] if mis_carros else [
        empty_state("Todavía no has publicado ningún carro.")
    ]

    # --- Subapartado 'Carros Ganados': subastas que este usuario ganó como
    # comprador y cuya entrega ya confirmó (ver
    # sistema.obtener_mis_carros_ganados). Mientras la entrega sigue
    # pendiente, ese mismo carro aparece únicamente en 'SUBASTAS ACTIVAS' →
    # 'Compras ganadas' (views/subastas_activas_view.py); en cuanto el
    # comprador la confirma, se "muda" para acá — Mis Carros pasa a
    # representar todo lo que el usuario posee, ya sea porque lo publicó
    # como vendedor o porque lo ganó y ya lo recibió. ---
    carros_ganados = sistema.obtener_mis_carros_ganados(usuario_actual.id)
    lista_ganados = [
        _fila_carro_ganado(c, sistema, usuario_actual, page, on_change) for c in carros_ganados
    ] if carros_ganados else [
        empty_state("Todavía no confirmaste la entrega de ningún carro que hayas ganado.")
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

            ft.Container(height=Sizes.GAP),
            ft.Divider(color=Colors.BORDER, height=1),
            ft.Container(height=Sizes.GAP),
            ft.Text("Carros Ganados", size=15, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text("Subastas que ganaste como comprador y cuya entrega ya confirmaste.",
                     size=12, color=Colors.TEXT_SECONDARY),
            ft.Container(height=12),
            *[item for c in lista_ganados for item in (c, ft.Container(height=12))],
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "MIS CARROS", body, sistema=sistema, on_nav_click=on_nav_click,
                       on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda,
                       on_messages_click=on_messages_click)
