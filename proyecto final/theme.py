"""
Paleta y estilos compartidos para la app de subastas.
Basado en las referencias de diseño (pantalla de login y dashboard).

Soporta modo oscuro (el original) y modo claro (Perfil -> Configuración ->
Apariencia). Colors sigue exponiendo los mismos nombres de siempre como
atributos de clase — nada de lo que ya existía en el resto del proyecto
tiene que cambiar la forma en que los usa (Colors.BACKGROUND, Colors.SURFACE,
etc.) — pero ahora un subconjunto de esos atributos se puede re-asignar en
caliente con Colors.aplicar_modo(modo_claro). Como todas las vistas leen
Colors.XXX en el momento en que se CONSTRUYEN (no una sola vez al importar),
alcanza con llamar aplicar_modo() y después reconstruir la pantalla que esté
activa (el mismo on_change / refrescar_vista_actual de siempre) para que el
cambio de tema se vea reflejado en todos lados sin tocar cada vista.
"""

import flet as ft


class Colors:
    # --- Lo único que cambia entre modo oscuro y modo claro. Los nombres
    # son los mismos que existían antes; lo que antes eran valores fijos
    # ahora son las dos paletas de abajo. ---
    _PALETA_OSCURA = {
        "BACKGROUND": "#13132B",       # fondo general (navy muy oscuro)
        "SURFACE": "#1A1A38",          # tarjetas / paneles
        "SURFACE_ALT": "#1E1E40",      # filas alternas, hover
        "BORDER": "#2A2A4D",           # bordes sutiles de tarjetas
        "TEXT_PRIMARY": "#FFFFFF",
        "TEXT_SECONDARY": "#9292B5",   # subtítulos, "+20% mes a mes", emails
        "TEXT_MUTED": "#6E6E8F",       # texto legal, placeholders oscuros
        "NAV_PILL_BG": "#FFFFFF",
        "NAV_PILL_TEXT": "#13132B",
        # Líneas y barras de los gráficos del dashboard. El nombre quedó de
        # cuando solo existía el modo oscuro (ahí sí eran blancas); en modo
        # claro este valor NO es blanco, ver _PALETA_CLARA.
        "LINE_WHITE": "#FFFFFF",
    }
    _PALETA_CLARA = {
        "BACKGROUND": "#E0E0E0",
        "SURFACE": "#FFFFFF",
        "SURFACE_ALT": "#EBEBEB",
        "BORDER": "#C6C6C6",
        "TEXT_PRIMARY": "#13132B",
        "TEXT_SECONDARY": "#4A4A63",
        "TEXT_MUTED": "#71718C",
        "NAV_PILL_BG": "#13132B",
        "NAV_PILL_TEXT": "#FFFFFF",
        "LINE_WHITE": "#13132B",
    }

    # --- Constantes que NO cambian entre modo claro/oscuro: acentos de
    # marca y colores de controles que ya funcionaban bien en ambos fondos. ---
    ACCENT_TEAL = "#3ED6C8"       # punto/resaltado en el gráfico de ingresos
    ACCENT_INDIGO = "#7C7CF0"     # links ("inicia sesion", términos), burbuja propia del chat
    INPUT_BG = "#FFFFFF"
    INPUT_TEXT = "#13132B"
    BUTTON_BG = "#0B0B1E"
    BUTTON_TEXT = "#FFFFFF"

    # Texto oscuro fijo para usar SIEMPRE sobre badges/burbujas de color
    # saturado (verde de "vendido"/"entregado", rojo de "no vendido", el
    # teal del ícono de mensajes, la burbuja propia del chat, etc.). Antes
    # varios de estos lugares reusaban Colors.BACKGROUND como "un color
    # oscuro cualquiera para texto legible sobre un fondo de color" — eso
    # funcionaba de casualidad porque BACKGROUND era oscuro en el único
    # tema que existía. Con el modo claro, BACKGROUND pasa a ser claro y
    # ese reuso se rompía (texto claro sobre un badge verde/rojo/teal,
    # ilegible), así que ahora ese uso tiene su propia constante fija.
    TEXT_ON_ACCENT = "#13132B"

    modo_claro = False

    @classmethod
    def aplicar_modo(cls, modo_claro: bool) -> None:
        """Cambia la paleta activa. No toca los acentos de marca ni los
        colores fijos de arriba a propósito (ver comentarios). Después de
        llamar esto hay que reconstruir la pantalla activa para que los
        controles ya creados tomen los valores nuevos — Flet no re-pinta
        solos los controles viejos, hay que volver a construir el árbol."""
        cls.modo_claro = modo_claro
        paleta = cls._PALETA_CLARA if modo_claro else cls._PALETA_OSCURA
        for nombre, valor in paleta.items():
            setattr(cls, nombre, valor)


# Arranca en modo oscuro (el comportamiento de siempre); main.py llama de
# nuevo a aplicar_modo() apenas carga la preferencia guardada en
# backend/data/preferencias.json, antes de construir la primera pantalla.
Colors.aplicar_modo(False)


class Sizes:
    CARD_RADIUS = 14
    INPUT_RADIUS = 8
    PAGE_PADDING = 32
    GAP = 20


def card(content, width=None, expand=None, padding=20, on_click=None):
    """Contenedor estándar tipo 'tarjeta' usado en todo el dashboard.
    Si se pasa on_click, la tarjeta se vuelve clickeable (con efecto ink)."""
    return ft.Container(
        content=content,
        bgcolor=Colors.SURFACE,
        border=ft.Border.all(width=1, color=Colors.BORDER),
        border_radius=Sizes.CARD_RADIUS,
        padding=padding,
        width=width,
        expand=expand,
        on_click=on_click,
        ink=on_click is not None,
    )
