"""
Punto de entrada de la app de subastas (Flet), conectada al backend real
y con las 5 pestañas funcionando (RESUMEN, MIS CARROS, EXPLORAR SUBASTAS,
SUBASTAS ACTIVAS, VENTAS).

Estructura del proyecto:
    main.py                        -> arranca la app, carga el backend, router de pestañas
    theme.py                       -> colores, tamaños y helpers de estilo
    backend/modelos.py             -> Usuario, Carro, Puja (modelo unificado)
    backend/sistema.py             -> AdministradorCompraVenta (lógica de negocio)
    backend/data/*.json            -> usuarios.json / carros.json / subastas.json
    views/shared.py                -> barra superior y helpers de UI compartidos
    views/login_view.py            -> registro / login
    views/dashboard_view.py        -> RESUMEN
    views/mis_carros_view.py       -> MIS CARROS (+ publicar carro nuevo)
    views/explorar_subastas_view.py-> EXPLORAR SUBASTAS (+ pujar)
    views/subastas_activas_view.py -> SUBASTAS ACTIVAS (mis pujas/favoritos)
    views/ventas_view.py           -> VENTAS (historial cerrado como vendedor)

Persistencia: cualquier acción que modifica datos (publicar carro, pujar)
guarda los 3 .json en backend/data/ inmediatamente después de aplicarse
(ver guardar_datos() y on_change más abajo).

Para correr:
    pip install -r requirements.txt
    python main.py
"""

import os

import flet as ft

from theme import Colors
from backend import AdministradorCompraVenta
from views.login_view import login_view
from views.dashboard_view import dashboard_view
from views.mis_carros_view import mis_carros_view
from views.explorar_subastas_view import explorar_subastas_view
from views.subastas_activas_view import subastas_activas_view
from views.ventas_view import ventas_view

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_USUARIOS = os.path.join(BASE_DIR, "backend", "data", "usuarios.json")
RUTA_CARROS = os.path.join(BASE_DIR, "backend", "data", "carros.json")
RUTA_PUJAS = os.path.join(BASE_DIR, "backend", "data", "subastas.json")

# Una entrada por cada pestaña de la barra de navegación.
VISTAS = {
    "RESUMEN": dashboard_view,
    "MIS CARROS": mis_carros_view,
    "EXPLORAR SUBASTAS": explorar_subastas_view,
    "SUBASTAS ACTIVAS": subastas_activas_view,
    "VENTAS": ventas_view,
}


def main(page: ft.Page):
    page.title = "App Subastas"
    page.bgcolor = Colors.BACKGROUND
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK

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

    usuario_actual = {"valor": None}  # usuario logueado en esta sesión
    estado_navegacion = {"tab": "RESUMEN"}

    def guardar_datos():
        sistema.guardar_datos_a_archivos(RUTA_USUARIOS, RUTA_CARROS, RUTA_PUJAS)

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
        page.add(constructor(page, sistema, usuario_actual["valor"],
                              on_nav_click=mostrar_vista, on_change=on_change))
        page.update()

    def show_login():
        page.controls.clear()
        page.add(login_view(page, sistema, on_login_success=handle_login_success))
        page.update()

    def handle_login_success(usuario):
        # Se llama tanto después de un registro nuevo como de un login exitoso.
        usuario_actual["valor"] = usuario
        guardar_datos()  # persiste el usuario nuevo (o nada, si fue solo login)
        mostrar_vista("RESUMEN")

    show_login()


if __name__ == "__main__":
    ft.app(target=main)
