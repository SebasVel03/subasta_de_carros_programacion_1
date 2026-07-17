"""
Punto de entrada de la app de subastas (Flet), conectada al backend real,
con las pestañas funcionando, búsqueda de subastas con filtros, panel de
detalle con galería de imágenes, chat comprador-vendedor, bandeja de
mensajes global, notificaciones del sistema (con aviso por correo cuando
corresponde), y soporte de múltiples cuentas en una misma sesión (persistida
entre reinicios).

Estructura del proyecto:
    main.py                        -> arranca la app, carga el backend, router de pestañas
    theme.py                       -> colores, tamaños y helpers de estilo
    backend/modelos.py             -> Usuario, Carro, Puja, Mensaje, Notificacion, Calificacion
    backend/sistema.py             -> AdministradorCompraVenta (lógica de negocio)
    backend/notificador_email.py   -> envío de correo cuando alguien no tiene la app abierta
    backend/data/usuarios.json     -> usuarios
    backend/data/carros.json       -> carros/subastas
    backend/data/subastas.json     -> pujas
    backend/data/mensajes.json     -> mensajes del chat comprador-vendedor
    backend/data/notificaciones.json -> avisos del sistema (ej. "te superaron una puja")
    backend/data/calificaciones.json -> reseñas de comprador sobre vendedor
    backend/data/sesion.json       -> qué cuentas estaban logueadas y cuál activa
    backend/data/preferencias.json -> apariencia (modo claro/oscuro), ver theme.py
    backend/data/config_email.json -> credenciales SMTP (copiar de config_email.example.json)
    views/shared.py                -> barra superior (con ícono de mensajes) y helpers de UI
    views/account_panel.py         -> mini panel de cuentas (clic en el avatar)
    views/bandeja_mensajes_dialog.py -> bandeja global de TODAS las conversaciones (clic en el ícono de mensajes)
    views/notificaciones_dialog.py -> panel de notificaciones (clic en la campana de Subastas Activas)
    views/detalle_subasta_dialog.py-> panel de detalle de una subasta, galería de imágenes, favoritos y calificación
    views/perfil_vendedor_dialog.py-> perfil público de un vendedor (solo lectura, con reseñas)
    views/chat_dialog.py           -> chat comprador-vendedor sobre un carro
    views/login_view.py            -> registro / login
    views/perfil_view.py           -> Perfil completo (info, configuración, cuentas)
    views/dashboard_view.py        -> RESUMEN
    views/mis_carros_view.py       -> MIS CARROS (+ publicar carro nuevo con varias fotos)
    views/explorar_subastas_view.py-> EXPLORAR SUBASTAS (+ pujar, + buscar, + filtros, + favoritos)
    views/subastas_activas_view.py -> SUBASTAS ACTIVAS (mis pujas/favoritos, compras ganadas, notificaciones)
    views/ventas_view.py           -> VENTAS (historial cerrado como vendedor)
    views/revision_view.py         -> REVISIÓN (solo admins)

Persistencia: cualquier acción que modifica datos (publicar carro, pujar,
mandar un mensaje, editar perfil) guarda los .json en backend/data/
inmediatamente después de aplicarse. Lo mismo pasa con la sesión.

Notificaciones (ver backend/sistema.py: registrar_puja / crear_notificacion):
cuando a alguien le superan una puja, SIEMPRE se genera una notificación
persistida (alimenta el badge de la campana en 'Subastas Activas'). Además:
  - Si esa cuenta está entre las que tienen sesión abierta en ESTA instancia
    de la app (cuentas_sesion), se le muestra un aviso emergente (SnackBar)
    la próxima vez que se reconstruya una pantalla bajo esa cuenta (ver
    avisar_notificaciones_nuevas más abajo) — se asume que "tiene la app
    abierta" porque está logueada acá mismo.
  - Si no, se asume que no tiene la app abierta ahora mismo y se le manda un
    correo (ver procesar_notificaciones_pendientes / backend/notificador_email.py),
    siempre que haya configuración SMTP cargada en backend/data/config_email.json.
Esta es la mejor aproximación posible con la arquitectura actual (archivos
JSON compartidos, sin sockets/push): si dos personas reales usan instancias
separadas de la app contra los mismos .json, cada instancia solo sabe qué
cuentas tiene logueadas ELLA, no las de la otra.

Para correr:
    pip install -r requirements.txt
    python main.py
"""

import json
import os

import flet as ft

from theme import Colors
from backend import AdministradorCompraVenta
from backend.notificador_email import cargar_configuracion_email, enviar_correo_notificacion
from views.login_view import login_view
from views.perfil_view import perfil_view
from views.account_panel import mostrar_panel_cuenta
from views.bandeja_mensajes_dialog import mostrar_bandeja_mensajes
from views.dashboard_view import dashboard_view
from views.mis_carros_view import mis_carros_view
from views.explorar_subastas_view import explorar_subastas_view
from views.subastas_activas_view import subastas_activas_view
from views.ventas_view import ventas_view
from views.revision_view import revision_view

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_USUARIOS = os.path.join(BASE_DIR, "backend", "data", "usuarios.json")
RUTA_CARROS = os.path.join(BASE_DIR, "backend", "data", "carros.json")
RUTA_PUJAS = os.path.join(BASE_DIR, "backend", "data", "subastas.json")
RUTA_MENSAJES = os.path.join(BASE_DIR, "backend", "data", "mensajes.json")
RUTA_SESION = os.path.join(BASE_DIR, "backend", "data", "sesion.json")
RUTA_PREFERENCIAS = os.path.join(BASE_DIR, "backend", "data", "preferencias.json")
RUTA_NOTIFICACIONES = os.path.join(BASE_DIR, "backend", "data", "notificaciones.json")
RUTA_CALIFICACIONES = os.path.join(BASE_DIR, "backend", "data", "calificaciones.json")
RUTA_CONFIG_EMAIL = os.path.join(BASE_DIR, "backend", "data", "config_email.json")

# Una entrada por cada pestaña de la barra de navegación. 'PERFIL' no está
# acá a propósito: no es una pestaña, se abre desde el mini panel de cuenta.
VISTAS = {
    "RESUMEN": dashboard_view,
    "MIS CARROS": mis_carros_view,
    "EXPLORAR SUBASTAS": explorar_subastas_view,
    "SUBASTAS ACTIVAS": subastas_activas_view,
    "VENTAS": ventas_view,
    "REVISIÓN": revision_view,
}

# Pestañas donde tiene sentido que el buscador filtre resultados en vivo.
VISTAS_CON_BUSQUEDA_ACTIVA = {"EXPLORAR SUBASTAS"}

# Tamaño mínimo de la ventana: por debajo de esto, varias tarjetas y la
# barra de navegación no alcanzan a acomodarse y se ven cortadas.
ANCHO_MINIMO = 980
ALTO_MINIMO = 680


def cargar_sesion(ruta):
    """Lee qué cuentas (ids) estaban logueadas y cuál era la activa.
    Si el archivo no existe o está corrupto, no rompe nada: simplemente
    se comporta como si no hubiera sesión guardada."""
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        return datos.get("cuentas_ids", []), datos.get("activa_id")
    except (FileNotFoundError, json.JSONDecodeError):
        return [], None


def guardar_sesion(ruta, cuentas_ids, activa_id):
    """No guarda contraseñas ni datos sensibles, solo ids de usuario."""
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({"cuentas_ids": cuentas_ids, "activa_id": activa_id}, f, ensure_ascii=False, indent=2)


def cargar_preferencias(ruta):
    """Lee la preferencia de apariencia (modo claro/oscuro) guardada de un
    cierre anterior. Si el archivo no existe o está corrupto, arranca en
    modo oscuro (el comportamiento de siempre) — mismo criterio tolerante
    que cargar_sesion()."""
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        return bool(datos.get("modo_claro", False))
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def guardar_preferencias(ruta, modo_claro):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({"modo_claro": modo_claro}, f, ensure_ascii=False, indent=2)


def main(page: ft.Page):
    # Apariencia: se aplica ANTES de construir cualquier pantalla, para que
    # la primera pantalla ya nazca con los colores correctos (si esto se
    # hiciera después, habría que reconstruir todo de nuevo apenas arranca).
    modo_claro_guardado = cargar_preferencias(RUTA_PREFERENCIAS)
    Colors.aplicar_modo(modo_claro_guardado)

    page.title = "App Subastas"
    page.bgcolor = Colors.BACKGROUND
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT if modo_claro_guardado else ft.ThemeMode.DARK
    page.window.min_width = ANCHO_MINIMO
    page.window.min_height = ALTO_MINIMO
    page.window.width = max(page.window.width or 0, ANCHO_MINIMO)
    page.window.height = max(page.window.height or 0, ALTO_MINIMO)

    # --- Backend: se carga una sola vez cuando arranca la app ---
    sistema = AdministradorCompraVenta()
    cargo_bien = sistema.cargar_datos_desde_archivos(
        RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS, RUTA_MENSAJES, RUTA_NOTIFICACIONES, RUTA_CALIFICACIONES,
    )
    if not cargo_bien:
        print("⚠️ No se pudieron cargar los datos iniciales. La app arranca sin datos.")

    # Configuración SMTP para las notificaciones por correo (ver
    # backend/notificador_email.py). Se carga UNA sola vez al arrancar; si
    # el archivo no existe o le falta algún campo, config_email queda en
    # None y enviar_correo_notificacion() simplemente no manda nada — la
    # app sigue funcionando igual, las notificaciones se siguen viendo
    # adentro (badge de Subastas Activas / panel de notificaciones).
    config_email = cargar_configuracion_email(RUTA_CONFIG_EMAIL)

    # Cierra automáticamente las subastas cuyo fecha_fin ya pasó. En una app
    # real esto debería correr periódicamente (ej. un job en segundo plano);
    # aquí se corre una vez al iniciar la app.
    cerradas = sistema.cerrar_subastas_vencidas()
    if cerradas:
        print(f"🔒 Se cerraron automáticamente {len(cerradas)} subasta(s) vencida(s): {cerradas}")
        sistema.guardar_datos_a_archivos(
            RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS, RUTA_MENSAJES, RUTA_NOTIFICACIONES, RUTA_CALIFICACIONES,
        )

    usuario_actual = {"valor": None}  # cuenta activa en este momento
    cuentas_sesion = []               # todas las cuentas con sesión iniciada (persiste en sesion.json)
    estado_navegacion = {"tab": "RESUMEN", "busqueda": "", "filtros": {}}

    def guardar_datos():
        sistema.guardar_datos_a_archivos(
            RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS, RUTA_MENSAJES, RUTA_NOTIFICACIONES, RUTA_CALIFICACIONES,
        )

    def persistir_sesion():
        ids = [u.id for u in cuentas_sesion]
        activa_id = usuario_actual["valor"].id if usuario_actual["valor"] else None
        guardar_sesion(RUTA_SESION, ids, activa_id)

    def handle_toggle_tema(modo_claro: bool):
        # Se llama desde el switch de "Modo claro" en Perfil -> Configuración
        # -> Apariencia (ver views/perfil_view.py). Colors.aplicar_modo()
        # solo reasigna los atributos de la clase; page.theme_mode/page.bgcolor
        # y la reconstrucción de la pantalla activa (refrescar_vista_actual)
        # son necesarios para que el cambio se vea reflejado de inmediato.
        Colors.aplicar_modo(modo_claro)
        page.theme_mode = ft.ThemeMode.LIGHT if modo_claro else ft.ThemeMode.DARK
        page.bgcolor = Colors.BACKGROUND
        guardar_preferencias(RUTA_PREFERENCIAS, modo_claro)
        refrescar_vista_actual()

    def handle_account_click():
        mostrar_panel_cuenta(
            page, usuario_actual["valor"], list(cuentas_sesion),
            on_switch_account=handle_switch_account,
            on_add_account=show_login,
            on_open_profile=mostrar_perfil,
            on_open_settings=mostrar_perfil,  # Configuración vive dentro del Perfil completo (misma pantalla)
            on_logout=handle_logout,
        )

    def handle_messages_click():
        # Bandeja global: TODAS las conversaciones del usuario activo, sin
        # importar el carro (ver views/bandeja_mensajes_dialog.py). Reusa
        # refrescar_vista_actual como on_change: al enviar un mensaje o abrir
        # una conversación (que la marca como leída), guarda a disco y
        # reconstruye la pantalla de fondo para que el badge del ícono de
        # mensajes quede al día apenas se cierre el diálogo.
        mostrar_bandeja_mensajes(page, sistema, usuario_actual["valor"], on_change=refrescar_vista_actual)

    def handle_search(texto: str):
        estado_navegacion["busqueda"] = texto
        # Buscar te lleva a Explorar Subastas si no estás ya en una pestaña
        # que sepa filtrar por texto (ahí es donde tiene sentido buscar carros).
        destino = estado_navegacion["tab"] if estado_navegacion["tab"] in VISTAS_CON_BUSQUEDA_ACTIVA else "EXPLORAR SUBASTAS"
        mostrar_vista(destino)

    def handle_filtros_change(nuevos_filtros: dict):
        # Mismo criterio que handle_search: el estado de los filtros vive acá
        # (no como variables locales dentro de explorar_subastas_view) para
        # que sobreviva a una reconstrucción de pantalla — por ejemplo,
        # después de pujar sobre uno de los resultados ya filtrados (ver
        # views/explorar_subastas_view.py: _panel_filtros).
        estado_navegacion["filtros"] = nuevos_filtros
        mostrar_vista("EXPLORAR SUBASTAS")

    def mostrar_vista(nombre_tab: str):
        # Cambiar de pestaña (a mano, con clic) limpia la búsqueda y los
        # filtros anteriores; solo se conservan cuando handle_search /
        # handle_filtros_change nos traen aquí a propósito (ambos pasan por
        # este mismo mostrar_vista, pero SIN cambiar antes estado_navegacion["tab"],
        # así que la condición de abajo no los pisa).
        if nombre_tab != estado_navegacion["tab"]:
            estado_navegacion["busqueda"] = ""
            estado_navegacion["filtros"] = {}
        estado_navegacion["tab"] = nombre_tab
        constructor = VISTAS.get(nombre_tab)
        if constructor is None:
            print(f"⚠️ No hay vista todavía para la pestaña '{nombre_tab}'.")
            return

        page.controls.clear()
        page.overlay.clear()
        page.add(constructor(page, sistema, usuario_actual["valor"],
                              on_nav_click=mostrar_vista, on_change=refrescar_vista_actual,
                              on_account_click=handle_account_click, on_search=handle_search,
                              valor_busqueda=estado_navegacion["busqueda"],
                              on_messages_click=handle_messages_click,
                              valor_filtros=estado_navegacion["filtros"],
                              on_filtros_change=handle_filtros_change))
        page.update()
        avisar_notificaciones_nuevas()

    def mostrar_perfil():
        estado_navegacion["tab"] = "PERFIL"

        page.controls.clear()
        page.overlay.clear()
        page.add(perfil_view(
            page, sistema, usuario_actual["valor"], cuentas_sesion=list(cuentas_sesion),
            on_nav_click=mostrar_vista, on_change=refrescar_vista_actual, on_account_click=handle_account_click,
            on_switch_account=handle_switch_account, on_add_account=show_login,
            on_logout=handle_logout, on_messages_click=handle_messages_click,
            on_toggle_tema=handle_toggle_tema, modo_claro=Colors.modo_claro,
        ))
        page.update()
        avisar_notificaciones_nuevas()

    def procesar_notificaciones_pendientes():
        """
        Revisa TODAS las notificaciones de la plataforma que todavía no se
        le 'avisaron' a nadie (ver sistema.obtener_todas_notificaciones_sin_avisar).
        Se llama después de guardar cualquier cambio (ver refrescar_vista_actual),
        así que corre después de CADA acción que muta datos, no solo después
        de pujar -- si dos personas usan instancias separadas de la app
        contra los mismos .json, esta instancia también procesa las
        notificaciones que generó la otra la próxima vez que guarde algo acá.

        Si el destinatario tiene una cuenta abierta en ESTA sesión
        (cuentas_sesion), se la deja para avisar_notificaciones_nuevas() (el
        aviso in-app). Si no, se asume que no tiene la app abierta ahora
        mismo y se le manda un correo (si hay configuración SMTP cargada).
        """
        pendientes = sistema.obtener_todas_notificaciones_sin_avisar()
        if not pendientes:
            return
        ids_con_sesion_abierta = {u.id for u in cuentas_sesion}
        for notif in pendientes:
            destino_id = notif["id_usuario_destino"]
            if destino_id in ids_con_sesion_abierta:
                continue  # se avisa in-app cuando corresponda, ver avisar_notificaciones_nuevas
            destinatario = sistema.usuarios.get(destino_id)
            if destinatario:
                ok, resultado = enviar_correo_notificacion(
                    config_email, destinatario.email,
                    asunto="App Subastas: novedades en tus subastas",
                    cuerpo=notif["texto"],
                )
                if not ok:
                    print(f"⚠️ No se pudo notificar por correo a {destinatario.email}: {resultado}")
            sistema.marcar_notificacion_avisada(notif["id"])

    def avisar_notificaciones_nuevas():
        """
        Si la cuenta activa tiene notificaciones que todavía no se le
        mostraron como aviso emergente (ver Notificacion.avisada_en_app en
        modelos.py), las muestra ahora con un SnackBar y las marca como
        avisadas -- así no se repite el mismo aviso en la próxima
        reconstrucción de pantalla. OJO: esto NO las marca como leídas (eso
        solo pasa al abrir el panel de notificaciones, ver
        views/notificaciones_dialog.py) -- el badge de la campana en
        'Subastas Activas' se mantiene aunque el SnackBar ya haya
        desaparecido de la pantalla.

        Se llama después de CUALQUIER reconstrucción de la pantalla
        principal (mostrar_vista), no solo tras pujar, porque una
        notificación puede haberse generado desde OTRA cuenta/instancia
        sobre los mismos .json.
        """
        usuario = usuario_actual["valor"]
        if not usuario:
            return
        nuevas = sistema.obtener_notificaciones_nuevas_sin_avisar(usuario.id)
        if not nuevas:
            return
        texto = nuevas[0]["texto"] if len(nuevas) == 1 else f"Tenés {len(nuevas)} novedades en tus subastas."
        page.overlay.append(ft.SnackBar(content=ft.Text(texto), bgcolor=Colors.SURFACE_ALT, open=True))
        sistema.marcar_notificaciones_avisadas(usuario.id)
        page.update()

    def refrescar_vista_actual():
        """Guarda a disco y reconstruye la pantalla que esté activa en este
        momento (una pestaña normal o el Perfil). Es el 'on_change' común a
        todas las vistas y diálogos: antes vivía duplicado como una closure
        anidada dentro de mostrar_vista() y otra dentro de mostrar_perfil();
        se centralizó acá para que también lo pueda usar handle_messages_click
        (la bandeja de mensajes no pertenece a ninguna pestaña puntual, así
        que necesita refrescar "lo que sea que esté de fondo" en vez de una
        vista fija)."""
        guardar_datos()
        procesar_notificaciones_pendientes()
        if estado_navegacion["tab"] == "PERFIL":
            mostrar_perfil()
        else:
            mostrar_vista(estado_navegacion["tab"])

    def show_login():
        page.controls.clear()
        page.overlay.clear()
        page.add(login_view(page, sistema, on_login_success=handle_login_success))
        page.update()

    def handle_login_success(usuario):
        # Se llama tanto después de un registro nuevo como de un login exitoso.
        # Si la cuenta no estaba ya en esta sesión, se agrega a la lista para
        # poder cambiar entre cuentas desde el panel de cuenta sin pedir
        # contraseña otra vez.
        if not any(u.id == usuario.id for u in cuentas_sesion):
            cuentas_sesion.append(usuario)
        usuario_actual["valor"] = usuario
        guardar_datos()
        persistir_sesion()
        mostrar_vista("RESUMEN")

    def handle_switch_account(usuario):
        usuario_actual["valor"] = usuario
        persistir_sesion()
        mostrar_vista("RESUMEN")

    def handle_logout():
        actual = usuario_actual["valor"]
        cuentas_sesion[:] = [u for u in cuentas_sesion if u.id != (actual.id if actual else None)]
        if cuentas_sesion:
            usuario_actual["valor"] = cuentas_sesion[0]
            persistir_sesion()
            mostrar_vista("RESUMEN")
        else:
            usuario_actual["valor"] = None
            persistir_sesion()  # deja sesion.json vacío -> al reabrir, pide login otra vez
            show_login()

    # --- Restaurar sesión guardada de un cierre anterior, si existe ---
    ids_guardados, activa_id_guardado = cargar_sesion(RUTA_SESION)
    for id_u in ids_guardados:
        usuario = sistema.usuarios.get(id_u)
        if usuario:  # si el usuario ya no existe (datos borrados/cambiados), simplemente se ignora
            cuentas_sesion.append(usuario)

    if cuentas_sesion:
        usuario_activo = sistema.usuarios.get(activa_id_guardado) if activa_id_guardado else None
        usuario_actual["valor"] = usuario_activo if usuario_activo in cuentas_sesion else cuentas_sesion[0]
        mostrar_vista("RESUMEN")
    else:
        show_login()


if __name__ == "__main__":
    ft.app(target=main)
