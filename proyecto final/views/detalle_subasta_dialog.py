"""
Panel de detalle de una subasta (se abre al hacer clic en cualquier tarjeta
de carro, desde Explorar Subastas, Subastas Activas, Mis Carros o Ventas).

Muestra la imagen ampliada y toda la información del vehículo, y adapta la
zona de acciones según quién está mirando:
  - El propio vendedor: ve sus conversaciones (quién le ha escrito) en vez
    de un formulario de puja.
  - Un postor, mientras la subasta está activa: formulario para pujar +
    botón para contactar al vendedor (preguntas antes de pujar).
  - El ganador de una subasta ya cerrada: aviso de que ganó + botón
    destacado para contactar al vendedor y coordinar la entrega, y — si
    todavía no lo hizo — un botón para confirmar que ya recibió el
    vehículo (ver sistema.confirmar_entrega en backend/sistema.py). Este
    mismo botón está disponible desde 'Subastas Activas' → 'Compras
    ganadas'; se repite acá para que también se pueda confirmar sin salir
    del detalle.
  - Cualquier otro espectador (subasta cerrada y no es su compra): solo
    información, sin acciones.

Además, si quien mira no es el propio vendedor, se muestra una fila con su
nombre/foto/reputación/verificación debajo del título; un clic ahí abre su
perfil público completo (views/perfil_vendedor_dialog.py) para que el
comprador pueda evaluar si es confiable antes de pujar, y un corazón para
agregar/quitar el carro de favoritos (ver sistema.agregar_favorito /
quitar_favorito en backend/sistema.py).

Si el carro tiene más de una foto (ver Carro.imagenes en modelos.py), debajo
de la imagen principal aparece una fila de miniaturas para cambiarla —
ver views/mis_carros_view.py para cómo se cargan al publicar.

Una vez que el comprador ganador confirmó la entrega, se le ofrece un
formulario para calificar al vendedor (1 a 5 estrellas + comentario
opcional, una sola vez por compra — ver sistema.calificar_vendedor).
"""

import flet as ft
from theme import Colors, card
from views.shared import money, estado_badge, auto_imagen, avatar_imagen
from views.chat_dialog import mostrar_chat
from views.perfil_vendedor_dialog import mostrar_perfil_vendedor


def _dato(etiqueta: str, valor: str) -> ft.Column:
    return ft.Column(
        [
            ft.Text(etiqueta, size=11, color=Colors.TEXT_SECONDARY),
            ft.Text(valor, size=13, color=Colors.TEXT_PRIMARY),
        ],
        spacing=2,
    )


def _tiempo_restante_texto(carro: dict) -> str:
    horas = carro.get("horas_restantes")
    if horas is None:
        return "Sin fecha de cierre"
    if horas <= 0:
        return "Cerrada"
    if horas < 48:
        return f"{horas:.0f} horas restantes"
    return f"{horas / 24:.0f} días restantes"


def _fila_conversacion(conv: dict, on_click) -> ft.Container:
    badge = (
        ft.Container(
            content=ft.Text(str(conv["no_leidos"]), size=11, color=Colors.TEXT_ON_ACCENT, weight=ft.FontWeight.W_600),
            bgcolor=Colors.ACCENT_TEAL, width=20, height=20, border_radius=10,
            alignment=ft.Alignment.CENTER,
        )
        if conv["no_leidos"] else ft.Container()
    )
    return ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(conv["otro_usuario_nombre"], size=13, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                        ft.Text(conv["ultimo_mensaje"], size=12, color=Colors.TEXT_SECONDARY,
                                 max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=2,
                    expand=True,
                ),
                badge,
            ],
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        border_radius=8,
        bgcolor=Colors.SURFACE_ALT,
        on_click=lambda e: on_click(conv["otro_usuario_id"]),
        ink=True,
    )


def _fila_vendedor(vendedor_info: dict, on_click) -> ft.Container:
    """Fila clickeable con foto/nombre/reputación/verificación del vendedor,
    debajo del título del carro. Abre su perfil público al hacer clic."""
    verificado = (
        ft.Icon(ft.Icons.VERIFIED, color=Colors.ACCENT_TEAL, size=16)
        if vendedor_info["verificado"] else ft.Container()
    )
    return ft.Container(
        content=ft.Row(
            [
                avatar_imagen(vendedor_info["foto_perfil"], size=32),
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(vendedor_info["nombre"], size=13, weight=ft.FontWeight.W_600,
                                         color=Colors.TEXT_PRIMARY),
                                verificado,
                            ],
                            spacing=4,
                        ),
                        ft.Text(f'{vendedor_info["reputacion"]} ⭐ · {vendedor_info["autos_vendidos"]} autos vendidos',
                                 size=11, color=Colors.TEXT_SECONDARY),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Colors.TEXT_SECONDARY, size=18),
            ],
            spacing=10,
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        border_radius=8,
        bgcolor=Colors.SURFACE_ALT,
        on_click=on_click,
        ink=True,
    )


def _fila_favorito(es_favorito: bool, on_click) -> ft.Container:
    """Corazón para agregar/quitar el carro de favoritos. Aparte de
    _fila_vendedor porque tiene que verse aunque el vendedor no tenga perfil
    público cargado (caso raro, datos rotos), y porque un postor puede
    querer marcar el favorito sin necesariamente entrar al perfil del
    vendedor."""
    return ft.IconButton(
        icon=ft.Icons.FAVORITE if es_favorito else ft.Icons.FAVORITE_BORDER,
        icon_color=Colors.ACCENT_TEAL if es_favorito else Colors.TEXT_SECONDARY,
        icon_size=22,
        tooltip="Quitar de favoritos" if es_favorito else "Agregar a favoritos",
        on_click=on_click,
    )


def _formulario_calificacion(sistema, usuario_actual, carro: dict, page: ft.Page, on_change) -> ft.Column:
    """Selector de 1 a 5 estrellas (clickeables) + comentario opcional, para
    que el comprador ganador califique al vendedor (ver
    sistema.calificar_vendedor en backend/sistema.py). Es estado local del
    diálogo hasta que se envía -- recién ahí se persiste."""
    estado_estrellas = {"valor": 5}
    feedback = ft.Text("", size=12, color="#E26A6A")
    estrella_botones: list[ft.IconButton] = []

    def _refrescar_estrellas():
        for i, boton in enumerate(estrella_botones, start=1):
            boton.icon = ft.Icons.STAR if i <= estado_estrellas["valor"] else ft.Icons.STAR_BORDER
            boton.icon_color = Colors.ACCENT_TEAL if i <= estado_estrellas["valor"] else Colors.TEXT_MUTED

    def handle_click_estrella(n):
        def handler(e):
            estado_estrellas["valor"] = n
            _refrescar_estrellas()
            page.update()
        return handler

    for i in range(1, 6):
        estrella_botones.append(ft.IconButton(
            icon=ft.Icons.STAR if i <= estado_estrellas["valor"] else ft.Icons.STAR_BORDER,
            icon_color=Colors.ACCENT_TEAL if i <= estado_estrellas["valor"] else Colors.TEXT_MUTED,
            icon_size=22,
            on_click=handle_click_estrella(i),
        ))

    comentario_f = ft.TextField(
        hint_text="Comentario (opcional)",
        multiline=True, min_lines=2, max_lines=3,
        bgcolor=Colors.SURFACE_ALT, border_color=Colors.BORDER, color=Colors.TEXT_PRIMARY,
    )

    def handle_enviar(e):
        ok, resultado = sistema.calificar_vendedor(
            carro["id"], usuario_actual.id, estado_estrellas["valor"], comentario_f.value or "",
        )
        if not ok:
            feedback.value = resultado
            page.update()
            return
        page.pop_dialog()
        if on_change:
            on_change()

    return ft.Column(
        [
            ft.Text("Calificar al vendedor", size=13, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
            ft.Row(estrella_botones, spacing=0),
            comentario_f,
            feedback,
            ft.Container(height=6),
            ft.ElevatedButton(
                content=ft.Text("Enviar calificación"),
                bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=handle_enviar,
            ),
        ],
        spacing=6,
    )


def mostrar_detalle_subasta(page: ft.Page, sistema, usuario_actual, carro: dict, on_change=None) -> None:
    es_vendedor = usuario_actual.id == carro["vendedor_id"]
    es_comprador_ganador = carro.get("comprador_id") == usuario_actual.id

    def cerrar_y_abrir_chat(otro_usuario_id: str):
        page.pop_dialog()
        page.update()
        mostrar_chat(page, sistema, usuario_actual, carro, otro_usuario_id, on_change)

    def cerrar_y_abrir_perfil_vendedor():
        page.pop_dialog()
        page.update()
        mostrar_perfil_vendedor(page, sistema, carro["vendedor_id"])

    # --- Galería: imagen principal + miniaturas clickeables (si hay más de
    # una foto). Es estado puramente visual/local a este diálogo -- cambiar
    # de miniatura no necesita on_change ni tocar sistema.py, solo redibuja
    # qué imagen se ve grande arriba. ---
    imagenes = carro.get("imagenes") or ([carro["imagen"]] if carro.get("imagen") else [])
    estado_galeria = {"indice": 0}
    imagen_principal = ft.Container(
        content=auto_imagen(imagenes[0] if imagenes else None, width=460, height=260, border_radius=12)
    )
    miniatura_containers: list[ft.Container] = []

    def _actualizar_bordes_miniaturas():
        for i, cont in enumerate(miniatura_containers):
            cont.border = ft.Border.all(2, Colors.ACCENT_TEAL) if i == estado_galeria["indice"] else None

    def handle_click_miniatura(indice):
        def handler(e):
            estado_galeria["indice"] = indice
            imagen_principal.content = auto_imagen(imagenes[indice], width=460, height=260, border_radius=12)
            _actualizar_bordes_miniaturas()
            page.update()
        return handler

    for i, img in enumerate(imagenes):
        miniatura_containers.append(
            ft.Container(
                content=auto_imagen(img, width=64, height=48, border_radius=6),
                on_click=handle_click_miniatura(i),
                ink=True,
                border_radius=6,
                padding=2,
                border=ft.Border.all(2, Colors.ACCENT_TEAL) if i == 0 else None,
            )
        )
    miniaturas = ft.Row(miniatura_containers, spacing=8, wrap=True) if len(imagenes) > 1 else ft.Container()

    es_favorito = carro["id"] in usuario_actual.favoritos

    def handle_toggle_favorito(e):
        if es_favorito:
            ok, resultado = sistema.quitar_favorito(usuario_actual.id, carro["id"])
        else:
            ok, resultado = sistema.agregar_favorito(usuario_actual.id, carro["id"])
        if ok:
            page.pop_dialog()
            if on_change:
                on_change()

    # --- Cabecera: imagen ampliada + miniaturas + título + estado (+ fila
    # del vendedor, salvo que quien mira sea el propio vendedor: no tiene
    # sentido que se linkee a su propio perfil desde acá, ni que se pueda
    # marcar su propio carro como favorito). ---
    vendedor_info = None if es_vendedor else sistema.obtener_perfil_publico_usuario(carro["vendedor_id"])

    titulo_fila: list[ft.Control] = [
        ft.Text(f'{carro["marca"]} {carro["modelo"]} ({carro["anio"]})',
                 size=18, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
    ]
    if not es_vendedor:
        titulo_fila.append(_fila_favorito(es_favorito, handle_toggle_favorito))
    titulo_fila.append(estado_badge(carro["estado_subasta"]))

    encabezado_controles: list[ft.Control] = [
        imagen_principal,
        ft.Container(height=8) if len(imagenes) > 1 else ft.Container(),
        miniaturas,
        ft.Container(height=12),
        ft.Row(titulo_fila, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
    ]
    if vendedor_info:
        encabezado_controles.append(ft.Container(height=10))
        encabezado_controles.append(_fila_vendedor(vendedor_info, lambda e: cerrar_y_abrir_perfil_vendedor()))

    encabezado = ft.Column(encabezado_controles, spacing=0)

    # --- Precio: la reserva solo se le muestra al vendedor/admin, nunca a
    # los postores (mostrarla les diría exactamente cuánto pujar para ganar
    # seguro, lo cual rompe el sentido de tener un precio de reserva). ---
    precio_label = "Precio final de venta" if carro["estado_subasta"] == "vendido" else "Puja más alta"
    precio_valor = carro["precio_final_venta"] if carro["estado_subasta"] == "vendido" else carro["puja_maxima"]

    precios_fila: list[ft.Control] = [
        _dato("Precio base", money(carro["precio_base"])),
        _dato(precio_label, money(precio_valor)),
        _dato("Kilometraje", f'{carro["kilometraje"]:,} km'),
        _dato("Tiempo", _tiempo_restante_texto(carro)),
    ]
    if es_vendedor or usuario_actual.rol == "admin":
        precios_fila.insert(2, _dato("Precio de reserva (solo tú lo ves)", money(carro["precio_reserva"])))

    especificaciones_txt = ", ".join(f"{k}: {v}" for k, v in carro["especificaciones"].items()) or "No especificadas"
    extras_txt = ", ".join(carro["extras"]) or "Ninguno"

    info_columna = ft.Column(
        [
            ft.Row(precios_fila, spacing=24, wrap=True, run_spacing=12),
            ft.Container(height=12),
            ft.Divider(color=Colors.BORDER, height=1),
            ft.Container(height=12),
            ft.Row([_dato("Especificaciones", especificaciones_txt)], spacing=24),
            ft.Container(height=8),
            ft.Row([_dato("Extras", extras_txt)], spacing=24),
            ft.Container(height=8),
            ft.Row(
                [
                    _dato("Condición declarada", carro.get("condicion_general") or "No especificada"),
                    _dato("Documentos", "✓ En regla" if carro.get("documentos_en_regla") else "Sin confirmar"),
                ],
                spacing=24,
            ),
            ft.Container(height=8),
            _dato("Descripción de daños", carro.get("descripcion_danos") or "Sin daños reportados"),
        ],
        spacing=0,
    )

    # --- Zona de acciones: cambia según quién está mirando ---
    acciones: list[ft.Control] = []

    if es_vendedor:
        conversaciones = sistema.obtener_conversaciones_carro(carro["id"], usuario_actual.id)
        acciones.append(ft.Text("Mensajes sobre este carro", size=13, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY))
        if conversaciones:
            for conv in conversaciones:
                acciones.append(_fila_conversacion(conv, cerrar_y_abrir_chat))
                acciones.append(ft.Container(height=6))
        else:
            acciones.append(ft.Text("Todavía nadie te ha escrito sobre este carro.", size=12, color=Colors.TEXT_SECONDARY))

    elif carro["estado_subasta"] == "activa":
        monto_field = ft.TextField(
            hint_text=f'> {money(carro["puja_maxima"])}',
            width=160, height=42, text_size=13,
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        )
        puja_feedback = ft.Text("", size=12, color="#E26A6A")

        def handle_pujar(e):
            try:
                monto = float(monto_field.value)
            except (TypeError, ValueError):
                puja_feedback.value = "Ingresa un monto válido."
                page.update()
                return
            ok, resultado = sistema.registrar_puja(usuario_actual.id, carro["id"], monto)
            if not ok:
                puja_feedback.value = resultado
                page.update()
                return
            # Tras una puja exitosa, los números de este diálogo (puja_maxima)
            # quedan desactualizados — se cierra y se refresca la lista de
            # donde vino, que sí va a mostrar el monto nuevo.
            page.pop_dialog()
            if on_change:
                on_change()

        acciones.extend([
            ft.Row(
                [
                    monto_field,
                    ft.ElevatedButton(
                        content=ft.Text("Pujar", size=13),
                        bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=handle_pujar,
                    ),
                    ft.OutlinedButton(
                        content=ft.Text("Contactar al vendedor", size=13),
                        on_click=lambda e: cerrar_y_abrir_chat(carro["vendedor_id"]),
                    ),
                ],
                spacing=10,
                wrap=True,
            ),
            puja_feedback,
        ])

    elif carro["estado_subasta"] == "vendido" and es_comprador_ganador:
        acciones.append(
            ft.Container(
                content=ft.Text("🎉 ¡Ganaste esta subasta!", size=14, weight=ft.FontWeight.BOLD, color=Colors.TEXT_ON_ACCENT),
                bgcolor="#7ED957", padding=ft.Padding.symmetric(horizontal=14, vertical=10), border_radius=8,
            )
        )
        acciones.append(ft.Container(height=10))
        acciones.append(
            ft.ElevatedButton(
                content=ft.Text("Contactar al vendedor para coordinar la entrega"),
                bgcolor=Colors.BUTTON_BG, color=Colors.BUTTON_TEXT,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=lambda e: cerrar_y_abrir_chat(carro["vendedor_id"]),
            )
        )
        acciones.append(ft.Container(height=10))

        # --- Confirmación de entrega física: mismo mecanismo que en
        # views/subastas_activas_view.py._fila_compra_ganada, repetido acá
        # para que también se pueda confirmar sin salir del detalle. ---
        if carro.get("entrega_confirmada"):
            acciones.append(
                ft.Text("✓ Ya confirmaste que recibiste este vehículo.", size=13, color="#7ED957")
            )
        else:
            entrega_feedback = ft.Text("", size=12, color="#E26A6A")

            def handle_confirmar_entrega(e):
                ok, resultado = sistema.confirmar_entrega(carro["id"], usuario_actual.id)
                if not ok:
                    entrega_feedback.value = resultado
                    page.update()
                    return
                page.pop_dialog()
                if on_change:
                    on_change()

            acciones.append(
                ft.OutlinedButton(
                    content=ft.Text("Marcar como entregado"),
                    on_click=handle_confirmar_entrega,
                )
            )
            acciones.append(entrega_feedback)

        # --- Calificación al vendedor: solo tiene sentido una vez que la
        # entrega ya se confirmó (no antes -- calificar antes de recibir el
        # auto no dice mucho), y una sola vez por compra (ver
        # sistema.ya_califico_compra / calificar_vendedor). ---
        if carro.get("entrega_confirmada"):
            acciones.append(ft.Container(height=14))
            if sistema.ya_califico_compra(carro["id"], usuario_actual.id):
                propia = next(
                    (c for c in sistema.obtener_calificaciones_usuario(carro["vendedor_id"])
                     if c["id_carro"] == carro["id"] and c["id_calificador"] == usuario_actual.id),
                    None,
                )
                estrellas_txt = "⭐" * propia["estrellas"] if propia else ""
                acciones.append(
                    ft.Text(f"Ya calificaste a este vendedor: {estrellas_txt}", size=13, color=Colors.ACCENT_TEAL)
                )
            else:
                acciones.append(_formulario_calificacion(sistema, usuario_actual, carro, page, on_change))

    elif carro["estado_subasta"] in ("vendido", "no_vendido"):
        mensaje = (
            f'Esta subasta ya cerró. Se vendió por {money(carro["precio_final_venta"])}.'
            if carro["estado_subasta"] == "vendido"
            else "Esta subasta cerró sin venderse."
        )
        acciones.append(ft.Text(mensaje, size=13, color=Colors.TEXT_SECONDARY))

    elif carro["estado_subasta"] == "rechazada":
        acciones.append(ft.Text(f'Publicación rechazada: {carro.get("motivo_rechazo") or "sin motivo registrado."}',
                                  size=13, color="#E26A6A"))
    else:  # pendiente_revision, visto por alguien que no es el vendedor (ej. admin)
        acciones.append(ft.Text("Esta subasta todavía está en revisión y no es pública.",
                                  size=13, color=Colors.TEXT_SECONDARY))

    def handle_cerrar(e):
        page.pop_dialog()
        page.update()

    dialog = ft.AlertDialog(
        modal=False,
        scrollable=True,
        bgcolor=Colors.SURFACE,
        content=ft.Container(
            width=480,
            content=ft.Column(
                [
                    encabezado,
                    ft.Container(height=16),
                    info_columna,
                    ft.Container(height=16),
                    ft.Divider(color=Colors.BORDER, height=1),
                    ft.Container(height=16),
                    ft.Column(acciones, spacing=0),
                ],
                spacing=0,
                tight=True,
            ),
        ),
        actions=[
            ft.TextButton(content=ft.Text("Cerrar", color=Colors.TEXT_SECONDARY), on_click=handle_cerrar),
        ],
    )

    page.show_dialog(dialog)
