"""
Paleta y estilos compartidos para la app de subastas.
Basado en las referencias de diseño (pantalla de login y dashboard).
"""

import flet as ft


class Colors:
    # Fondos
    BACKGROUND = "#13132B"       # fondo general (navy muy oscuro)
    SURFACE = "#1A1A38"          # tarjetas / paneles
    SURFACE_ALT = "#1E1E40"      # filas alternas, hover
    BORDER = "#2A2A4D"           # bordes sutiles de tarjetas

    # Texto
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#9292B5"   # subtítulos, "+20% mes a mes", emails
    TEXT_MUTED = "#6E6E8F"       # texto legal, placeholders oscuros

    # Acentos
    ACCENT_TEAL = "#3ED6C8"      # punto/resaltado en el gráfico de ingresos
    ACCENT_INDIGO = "#7C7CF0"    # links ("inicia sesion", términos)
    LINE_WHITE = "#FFFFFF"       # líneas y barras de los gráficos

    # Controles
    INPUT_BG = "#FFFFFF"
    INPUT_TEXT = "#13132B"
    BUTTON_BG = "#0B0B1E"
    BUTTON_TEXT = "#FFFFFF"
    NAV_PILL_BG = "#FFFFFF"
    NAV_PILL_TEXT = "#13132B"


class Sizes:
    CARD_RADIUS = 14
    INPUT_RADIUS = 8
    PAGE_PADDING = 32
    GAP = 20


def card(content, width=None, expand=None, padding=20):
    """Contenedor estándar tipo 'tarjeta' usado en todo el dashboard."""
    return ft.Container(
        content=content,
        bgcolor=Colors.SURFACE,
        border=ft.Border.all(width=1, color=Colors.BORDER),
        border_radius=Sizes.CARD_RADIUS,
        padding=padding,
        width=width,
        expand=expand,
    )
