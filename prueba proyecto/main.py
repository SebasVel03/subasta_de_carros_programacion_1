"""
Punto de entrada de la app de subastas (Flet), conectada al backend real,
con las pestañas funcionando y soporte de múltiples cuentas en una misma
sesión (cambiar de cuenta, agregar otra, cerrar sesión) desde la pantalla
de Perfil. Esa sesión (qué cuentas estaban abiertas y cuál era la activa)
se guarda en disco, así que persiste entre reinicios de la app.

Estructura del proyecto:
    main.py                        -> arranca la app, carga el backend, router de pestañas
    theme.py                       -> colores, tamaños y helpers de estilo
    backend/modelos.py             -> Usuario, Carro, Puja (modelo unificado)
    backend/sistema.py             -> AdministradorCompraVenta (lógica de negocio)
    backend/data/usuarios.json     -> usuarios
    backend/data/carros.json       -> carros/subastas
    backend/data/subastas.json     -> pujas
    backend/data/sesion.json       -> qué cuentas estaban logueadas y cuál activa (NUEVO)
    views/shared.py                -> barra superior y helpers de UI compartidos
    views/login_view.py            -> registro / login
    views/perfil_view.py           -> Perfil (info, configuración, cambiar de cuenta)
    views/dashboard_view.py        -> RESUMEN
    views/mis_carros_view.py       -> MIS CARROS (+ publicar carro nuevo)
    views/explorar_subastas_view.py-> EXPLORAR SUBASTAS (+ pujar)
    views/subastas_activas_view.py -> SUBASTAS ACTIVAS (mis pujas/favoritos)
    views/ventas_view.py           -> VENTAS (historial cerrado como vendedor)
    views/revision_view.py         -> REVISIÓN (solo admins)

Persistencia: cualquier acción que modifica datos (publicar carro, pujar,
editar perfil) guarda los .json en backend/data/ inmediatamente después de
aplicarse. Lo mismo pasa con la sesión: cada vez que se agrega, cambia o
cierra una cuenta, se reescribe sesion.json (ver guardar_sesion() abajo).
No se guarda ninguna contraseña ahí, solo los ids de usuario — la cuenta
sigue necesitando su contraseña real la primera vez que se registra/inicia
sesión en esta máquina; lo que persiste es "no me vuelvas a pedir login
mientras la app recuerde esta sesión".

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
RUTA_SESION = os.path.join(BASE_DIR, "backend", "data", "sesion.json")

# Una entrada por cada pestaña de la barra de navegación. 'PERFIL' no está
# acá a propósito: no es una pestaña, se abre haciendo clic en el avatar.
VISTAS = {
    "RESUMEN": dashboard_view,
    "MIS CARROS": mis_carros_view,
    "EXPLORAR SUBASTAS": explorar_subastas_view,
    "SUBASTAS ACTIVAS": subastas_activas_view,
    "VENTAS": ventas_view,
    "REVISIÓN": revision_view,
}

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
    cargo_bien = sistema.cargar_datos_desde_archivos(RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS)
    if not cargo_bien:
        print("⚠️ No se pudieron cargar los datos iniciales. La app arranca sin datos.")

    # Cierra automáticamente las subastas cuyo fecha_fin ya pasó. En una app
    # real esto debería correr periódicamente (ej. un job en segundo plano);
    # aquí se corre una vez al iniciar la app.
    cerradas = sistema.cerrar_subastas_vencidas()
    if cerradas:
        print(f"🔒 Se cerraron automáticamente {len(cerradas)} subasta(s) vencida(s): {cerradas}")
        sistema.guardar_datos_a_archivos(RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS)

    usuario_actual = {"valor": None}  # cuenta activa en este momento
    cuentas_sesion = []               # todas las cuentas con sesión iniciada (persiste en sesion.json)
    estado_navegacion = {"tab": "RESUMEN"}

    def guardar_datos():
        sistema.guardar_datos_a_archivos(RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS)

    def persistir_sesion():
        ids = [u.id for u in cuentas_sesion]
        activa_id = usuario_actual["valor"].id if usuario_actual["valor"] else None
        guardar_sesion(RUTA_SESION, ids, activa_id)

    def mostrar_vista(nombre_tab: str):
        estado_navegacion["tab"] = nombre_tab
        constructor = VISTAS.get(nombre_tab)
        if constructor is None:
            print(f"⚠️ No hay vista todavía para la pestaña '{nombre_tab}'.")
            return

        def on_change():
            # Se llama después de cualquier acción que modificó datos
            # (publicar carro, pujar): primero persiste a disco, luego
            # reconstruye la vista actual para reflejar el cambio.
            guardar_datos()
            mostrar_vista(estado_navegacion["tab"])

        page.controls.clear()
        page.overlay.clear()
        page.add(constructor(page, sistema, usuario_actual["valor"],
                              on_nav_click=mostrar_vista, on_change=on_change,
                              on_profile_click=mostrar_perfil))
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
            on_nav_click=mostrar_vista, on_change=on_change, on_profile_click=mostrar_perfil,
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
        # poder cambiar entre cuentas desde Perfil sin pedir contraseña otra vez.
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
