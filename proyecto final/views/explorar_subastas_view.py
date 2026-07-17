"""
Pestaña 'EXPLORAR SUBASTAS'.

Muestra las subastas activas de la plataforma (no solo las del usuario).
Cada tarjeta es clickeable y abre el panel de detalle con la imagen ampliada
y toda la info del carro (ver views/detalle_subasta_dialog.py); pujar
también se puede hacer directo desde la tarjeta, sin abrir el detalle.
El cuadro de búsqueda de la barra superior filtra por marca/modelo/año.

Además tiene:
- Un corazón para agregar/quitar el carro de favoritos (ver
  sistema.agregar_favorito / quitar_favorito en backend/sistema.py). Un
  carro favorito aparece en 'SUBASTAS ACTIVAS' con el estado "Solo en
  favoritos" aunque nunca se haya pujado por él (ver
  sistema.obtener_mis_subastas_activas).
- Un panel de filtros (marca, rango de precio actual, rango de año, orden)
  que se combina con el buscador de texto de la barra superior — ver
  sistema.obtener_subastas_explorar y _panel_filtros más abajo. El estado
  de los filtros vive centralizado en main.py (estado_navegacion["filtros"])
  para que sobreviva a una reconstrucción de pantalla (ej. después de
  pujar), igual que ya pasa con el texto de búsqueda.
"""

import flet as ft
from theme import Colors, Sizes, card
from views.shared import page_shell, money, empty_state, auto_imagen
from views.detalle_subasta_dialog import mostrar_detalle_subasta

ORDENES_DISPONIBLES = [
    ("cierra_pronto", "Cierra pronto"),
    ("precio_asc", "Precio: menor a mayor"),
    ("precio_desc", "Precio: mayor a menor"),
    ("mas_pujas", "Más pujas"),
]


def _fila_subasta(c: dict, sistema, usuario_actual, page, on_change) -> ft.Container:
    monto_field = ft.TextField(
        hint_text=f'> {money(c["puja_maxima"])}',
        width=140,
        height=42,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        text_size=13,
    )
    feedback = ft.Text("", size=12)

    def handle_pujar(e):
        try:
            monto = float(monto_field.value)
        except (TypeError, ValueError):
            feedback.value = "Ingresa un monto válido."
            feedback.color = "#E26A6A"
            page.update()
            return

        ok, resultado = sistema.registrar_puja(usuario_actual.id, c["id"], monto)
        if not ok:
            feedback.value = resultado
            feedback.color = "#E26A6A"
            page.update()
            return

        if on_change:
            on_change()  # guarda y reconstruye la vista con la nueva puja_maxima

    def handle_abrir_detalle(e):
        mostrar_detalle_subasta(page, sistema, usuario_actual, c, on_change)

    es_favorito = c["id"] in usuario_actual.favoritos

    def handle_toggle_favorito(e):
        if es_favorito:
            ok, resultado = sistema.quitar_favorito(usuario_actual.id, c["id"])
        else:
            ok, resultado = sistema.agregar_favorito(usuario_actual.id, c["id"])
        if ok and on_change:
            on_change()

    favorito_btn = ft.IconButton(
        icon=ft.Icons.FAVORITE if es_favorito else ft.Icons.FAVORITE_BORDER,
        icon_color=Colors.ACCENT_TEAL if es_favorito else Colors.TEXT_SECONDARY,
        icon_size=20,
        tooltip="Quitar de favoritos" if es_favorito else "Agregar a favoritos",
        on_click=handle_toggle_favorito,
    )

    horas = c["horas_restantes"]
    tiempo_txt = f'{horas:.0f} h restantes' if horas is not None and horas < 48 else (
        f'{horas / 24:.0f} d restantes' if horas is not None else 'sin fecha de cierre'
    )

    pujar_btn = ft.ElevatedButton(
        content=ft.Text("Pujar", size=13),
        bgcolor=Colors.BUTTON_BG,
        color=Colors.BUTTON_TEXT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=handle_pujar,
        disabled=c["es_propio"],
    )

    controles_derecha: list[ft.Control] = (
        [ft.Text("Es tu propio carro", size=12, color=Colors.TEXT_SECONDARY)]
        if c["es_propio"] else
        [monto_field, pujar_btn]
    )

    # La imagen y el texto abren el detalle; los controles de puja y el
    # corazón de favorito (cada uno en su propio Container) no, para que
    # hacer clic ahí no dispare accidentalmente la apertura del panel
    # completo — mismo patrón que ya usa el resto de las tarjetas del
    # proyecto (ver detalle_subasta_dialog.py / subastas_activas_view.py).
    contenido: list[ft.Control] = [
        ft.Row(
            [
                ft.Container(
                    content=auto_imagen(c.get("imagen"), width=90, height=68),
                    on_click=handle_abrir_detalle,
                    ink=True,
                    border_radius=8,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f'{c["marca"]} {c["modelo"]} ({c["anio"]})',
                                     size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                            ft.Text(f'{c["kilometraje"]:,} km · {c["num_pujas"]} pujas · {tiempo_txt}',
                                     size=12, color=Colors.TEXT_SECONDARY),
                        ],
                        spacing=2,
                    ),
                    on_click=handle_abrir_detalle,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Puja más alta", size=11, color=Colors.TEXT_SECONDARY),
                            ft.Text(money(c["puja_maxima"]), size=16, weight=ft.FontWeight.BOLD,
                                     color=Colors.TEXT_PRIMARY),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=0,
                    ),
                    on_click=handle_abrir_detalle,
                ),
                favorito_btn,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=8,
        ),
        ft.Container(height=10),
        ft.Row(controles_derecha, alignment=ft.MainAxisAlignment.END, spacing=10),
        feedback,
    ]

    return card(
        ft.Column(contenido, spacing=0),
        padding=16,
    )


def _panel_filtros(page: ft.Page, filtros: dict, marcas_disponibles: list, on_filtros_change) -> ft.Container:
    """
    Panel de filtros de 'Explorar Subastas': marca, rango de precio actual
    (puja más alta de cada carro, no precio_base), rango de año, y orden.
    Se aplica con un botón explícito (no en cada tecla) para no reconstruir
    toda la pantalla en cada carácter tipeado — mismo criterio que el
    buscador de texto de la barra superior, que también aplica con Enter.

    filtros llega tal cual está guardado en main.py (estado_navegacion),
    y on_filtros_change(nuevo_dict) es lo que main.py usa para actualizarlo
    y reconstruir esta pestaña con el resultado ya filtrado.
    """
    marca_f = ft.Dropdown(
        label="Marca",
        width=160,
        options=[ft.DropdownOption(text="Todas", key="__todas__")] +
                [ft.DropdownOption(text=m, key=m) for m in marcas_disponibles],
        value=filtros.get("marca") or "__todas__",
    )
    precio_min_f = ft.TextField(
        label="Precio mín.", width=120,
        value="" if filtros.get("precio_min") is None else str(int(filtros["precio_min"])),
    )
    precio_max_f = ft.TextField(
        label="Precio máx.", width=120,
        value="" if filtros.get("precio_max") is None else str(int(filtros["precio_max"])),
    )
    anio_min_f = ft.TextField(
        label="Año desde", width=110,
        value="" if filtros.get("anio_min") is None else str(filtros["anio_min"]),
    )
    anio_max_f = ft.TextField(
        label="Año hasta", width=110,
        value="" if filtros.get("anio_max") is None else str(filtros["anio_max"]),
    )
    orden_f = ft.Dropdown(
        label="Ordenar por",
        width=190,
        options=[ft.DropdownOption(text=etiqueta, key=clave) for clave, etiqueta in ORDENES_DISPONIBLES],
        value=filtros.get("orden", "cierra_pronto"),
    )
    feedback = ft.Text("", size=12, color="#E26A6A")

    def _a_numero(valor, tipo):
        valor = (valor or "").strip()
        if not valor:
            return None, True
        try:
            return tipo(valor), True
        except ValueError:
            return None, False

    def handle_aplicar(e):
        precio_min, ok1 = _a_numero(precio_min_f.value, float)
        precio_max, ok2 = _a_numero(precio_max_f.value, float)
        anio_min, ok3 = _a_numero(anio_min_f.value, int)
        anio_max, ok4 = _a_numero(anio_max_f.value, int)
        if not (ok1 and ok2 and ok3 and ok4):
            feedback.value = "Los precios y años tienen que ser números."
            page.update()
            return
        feedback.value = ""
        nuevos_filtros = {
            "marca": None if marca_f.value in (None, "__todas__") else marca_f.value,
            "precio_min": precio_min,
            "precio_max": precio_max,
            "anio_min": anio_min,
            "anio_max": anio_max,
            "orden": orden_f.value or "cierra_pronto",
        }
        if on_filtros_change:
            on_filtros_change(nuevos_filtros)

    def handle_limpiar(e):
        if on_filtros_change:
            on_filtros_change({})

    return card(
        ft.Column(
            [
                ft.Text("Filtros", size=12, weight=ft.FontWeight.W_600, color=Colors.TEXT_SECONDARY),
                ft.Container(height=8),
                ft.Row(
                    [marca_f, precio_min_f, precio_max_f, anio_min_f, anio_max_f, orden_f],
                    spacing=12, wrap=True, run_spacing=10,
                ),
                feedback,
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            content=ft.Text("Aplicar filtros"),
                            bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=handle_aplicar,
                        ),
                        ft.OutlinedButton(content=ft.Text("Limpiar filtros"), on_click=handle_limpiar),
                    ],
                    spacing=10,
                ),
            ],
            spacing=0,
        ),
        padding=16,
    )


def explorar_subastas_view(page: ft.Page, sistema, usuario_actual, on_nav_click=None, on_change=None,
                            on_account_click=None, on_search=None, valor_busqueda="",
                            on_messages_click=None, valor_filtros=None, on_filtros_change=None) -> ft.Container:
    filtros = valor_filtros or {}
    subastas = sistema.obtener_subastas_explorar(
        id_usuario=usuario_actual.id,
        filtro_texto=valor_busqueda or None,
        marca=filtros.get("marca"),
        precio_min=filtros.get("precio_min"),
        precio_max=filtros.get("precio_max"),
        anio_min=filtros.get("anio_min"),
        anio_max=filtros.get("anio_max"),
        orden=filtros.get("orden", "cierra_pronto"),
    )
    marcas_disponibles = sistema.obtener_marcas_activas()

    if subastas:
        filas = [_fila_subasta(c, sistema, usuario_actual, page, on_change) for c in subastas]
        lista = [item for c in filas for item in (c, ft.Container(height=12))]
    elif valor_busqueda or filtros:
        lista = [empty_state("Ninguna subasta activa coincide con la búsqueda y/o los filtros aplicados.")]
    else:
        lista = [empty_state("No hay subastas activas en la plataforma por ahora.")]

    body = ft.Column(
        [
            ft.Text("Explorar Subastas", size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Text("Todas las subastas activas del mercado.", size=13, color=Colors.TEXT_SECONDARY),
            ft.Container(height=Sizes.GAP),
            _panel_filtros(page, filtros, marcas_disponibles, on_filtros_change),
            ft.Container(height=Sizes.GAP),
            *lista,
        ],
        spacing=0,
    )

    return page_shell(usuario_actual, "EXPLORAR SUBASTAS", body, sistema=sistema, on_nav_click=on_nav_click,
                       on_account_click=on_account_click, on_search=on_search, valor_busqueda=valor_busqueda,
                       on_messages_click=on_messages_click)
