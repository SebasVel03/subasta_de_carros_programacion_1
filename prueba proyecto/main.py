"""
Punto de entrada de la app de subastas (Flet), conectada al backend real,
con las pestañas funcionando, búsqueda de subastas, panel de detalle con
imagen ampliada, chat comprador-vendedor, y soporte de múltiples cuentas
en una misma sesión (persistida entre reinicios).

Estructura del proyecto:
    main.py                        -> arranca la app, carga el backend, router de pestañas
    theme.py                       -> colores, tamaños y helpers de estilo
    backend/modelos.py             -> Usuario, Carro, Puja, Mensaje (modelo unificado)
    backend/sistema.py             -> AdministradorCompraVenta (lógica de negocio)
    backend/data/usuarios.json     -> usuarios
    backend/data/carros.json       -> carros/subastas
    backend/data/subastas.json     -> pujas
    backend/data/mensajes.json     -> mensajes del chat comprador-vendedor
    backend/data/sesion.json       -> qué cuentas estaban logueadas y cuál activa
    views/shared.py                -> barra superior (sin los 3 puntos) y helpers de UI
    views/account_panel.py         -> mini panel de cuentas (clic en el avatar)
    views/detalle_subasta_dialog.py-> panel de detalle de una subasta + imagen ampliada
    views/chat_dialog.py           -> chat comprador-vendedor sobre un carro
    views/login_view.py            -> registro / login
    views/perfil_view.py           -> Perfil completo (info, configuración, cuentas)
    views/dashboard_view.py        -> RESUMEN
    views/mis_carros_view.py       -> MIS CARROS (+ publicar carro nuevo)
    views/explorar_subastas_view.py-> EXPLORAR SUBASTAS (+ pujar, + buscar)
    views/subastas_activas_view.py -> SUBASTAS ACTIVAS (mis pujas/favoritos, compras ganadas)
    views/ventas_view.py           -> VENTAS (historial cerrado como vendedor)
    views/revision_view.py         -> REVISIÓN (solo admins)

Persistencia: cualquier acción que modifica datos (publicar carro, pujar,
mandar un mensaje, editar perfil) guarda los .json en backend/data/
inmediatamente después de aplicarse. Lo mismo pasa con la sesión.

Para correr:
    pip install -r requirements.txt
    python main.py
"""

import json
import os

import flet as ft

from theme import Colors
from backend import AdministradorCompraVenta
from views.login_view import login_view
from views.perfil_view import perfil_view
from views.account_panel import mostrar_panel_cuenta
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


def main(page: ft.Page):
    page.title = "App Subastas"
    page.bgcolor = Colors.BACKGROUND
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.window.min_width = ANCHO_MINIMO
    page.window.min_height = ALTO_MINIMO
    page.window.width = max(page.window.width or 0, ANCHO_MINIMO)
    page.window.height = max(page.window.height or 0, ALTO_MINIMO)

    # --- Backend: se carga una sola vez cuando arranca la app ---
    sistema = AdministradorCompraVenta()
    cargo_bien = sistema.cargar_datos_desde_archivos(RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS, RUTA_MENSAJES)
    if not cargo_bien:
        print("⚠️ No se pudieron cargar los datos iniciales. La app arranca sin datos.")

    # Cierra automáticamente las subastas cuyo fecha_fin ya pasó. En una app
    # real esto debería correr periódicamente (ej. un job en segundo plano);
    # aquí se corre una vez al iniciar la app.
    cerradas = sistema.cerrar_subastas_vencidas()
    if cerradas:
        print(f"🔒 Se cerraron automáticamente {len(cerradas)} subasta(s) vencida(s): {cerradas}")
        sistema.guardar_datos_a_archivos(RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS, RUTA_MENSAJES)

    usuario_actual = {"valor": None}  # cuenta activa en este momento
    cuentas_sesion = []               # todas las cuentas con sesión iniciada (persiste en sesion.json)
    estado_navegacion = {"tab": "RESUMEN", "busqueda": ""}

    def guardar_datos():
        sistema.guardar_datos_a_archivos(RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS, RUTA_MENSAJES)

    def persistir_sesion():
        ids = [u.id for u in cuentas_sesion]
        activa_id = usuario_actual["valor"].id if usuario_actual["valor"] else None
        guardar_sesion(RUTA_SESION, ids, activa_id)

    def handle_account_click():
        mostrar_panel_cuenta(
            page, usuario_actual["valor"], list(cuentas_sesion),
            on_switch_account=handle_switch_account,
            on_add_account=show_login,
            on_open_profile=mostrar_perfil,
            on_open_settings=mostrar_perfil,  # Configuración vive dentro del Perfil completo (misma pantalla)
            on_logout=handle_logout,
        )

    def handle_search(texto: str):
        estado_navegacion["busqueda"] = texto
        # Buscar te lleva a Explorar Subastas si no estás ya en una pestaña
        # que sepa filtrar por texto (ahí es donde tiene sentido buscar carros).
        destino = estado_navegacion["tab"] if estado_navegacion["tab"] in VISTAS_CON_BUSQUEDA_ACTIVA else "EXPLORAR SUBASTAS"
        mostrar_vista(destino)

    def mostrar_vista(nombre_tab: str):
        # Cambiar de pestaña (a mano, con clic) limpia la búsqueda anterior;
        # solo se conserva cuando handle_search nos trae aquí a propósito.
        if nombre_tab != estado_navegacion["tab"]:
            estado_navegacion["busqueda"] = ""
        estado_navegacion["tab"] = nombre_tab
        constructor = VISTAS.get(nombre_tab)
        if constructor is None:
            print(f"⚠️ No hay vista todavía para la pestaña '{nombre_tab}'.")
            return

        def on_change():
            # Se llama después de cualquier acción que modificó datos
            # (publicar carro, pujar, enviar un mensaje): primero persiste a
            # disco, luego reconstruye la vista actual para reflejar el cambio.
            guardar_datos()
            mostrar_vista(estado_navegacion["tab"])

        page.controls.clear()
        page.overlay.clear()
        page.add(constructor(page, sistema, usuario_actual["valor"],
                              on_nav_click=mostrar_vista, on_change=on_change,
                              on_account_click=handle_account_click, on_search=handle_search,
                              valor_busqueda=estado_navegacion["busqueda"]))
        page.update()

    def mostrar_perfil():
        estado_navegacion["tab"] = "PERFIL"

        def on_change():
            guardar_datos()
            mostrar_perfil()

        page.controls.clear()
        page.overlay.clear()
        page.add(perfil_view(
            page, sistema, usuario_actual["valor"], cuentas_sesion=list(cuentas_sesion),
            on_nav_click=mostrar_vista, on_change=on_change, on_account_click=handle_account_click,
            on_switch_account=handle_switch_account, on_add_account=show_login,
            on_logout=handle_logout,
        ))
        page.update()

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
