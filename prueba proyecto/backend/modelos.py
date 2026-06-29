"""
Modelos de datos UNIFICADOS para la app de subastas de carros.

Antes había dos modelos de "persona" (Cliente en Clase_Cliente.py / Clase_Carro.py,
y Usuario en admin.py) y dos modelos de "Carro" distintos e incompatibles entre sí.
Este archivo reemplaza a los dos: de aquí en adelante solo existe UN Usuario y UN Carro,
con los campos que realmente vienen en usuarios.json / carros.json.

Los archivos Clase_Carro.py, Clase_Cliente.py y Cliente_Registro.py quedan
obsoletos y se pueden borrar del proyecto: su lógica útil (favoritos,
historial de ofertas) se incorporó aquí dentro de Usuario.
"""

import hashlib
from datetime import datetime, timezone


def hash_password(password: str) -> str:
    """
    Hash simple de la contraseña con SHA-256.

    NOTA PARA EL EQUIPO: esto es suficiente para el proyecto académico, pero
    NO es seguro para producción real. Para un proyecto en producción usar
    bcrypt o argon2 con un salt distinto por usuario (passlib, bcrypt, etc.).
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parsear_fecha(fecha_iso):
    """Convierte un string ISO ('...Z' incluido) a datetime con timezone."""
    if not fecha_iso:
        return None
    return datetime.fromisoformat(fecha_iso.replace("Z", "+00:00"))


class Usuario:
    """
    Reemplaza tanto a la vieja clase `Cliente` como a la vieja clase `Usuario`
    de admin.py. Incluye favoritos e historial de ofertas (que antes vivían
    en Cliente y nunca se conectaban con el resto del sistema).
    """

    def __init__(self, id_usuario, nombre, email, password_hash, rol,
                 telefono="", verificado=False, autos_en_posesion=None,
                 reputacion=0.0, historial_ofertas=None, favoritos=None,
                 fecha_registro=None):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash
        self.rol = rol  # 'vendedor' o 'postor'
        self.telefono = telefono
        self.verificado = verificado
        self.autos_en_posesion = autos_en_posesion if autos_en_posesion is not None else []
        self.reputacion = reputacion
        self.historial_ofertas = historial_ofertas if historial_ofertas is not None else []
        self.favoritos = favoritos if favoritos is not None else []  # ids de carros
        self.fecha_registro = fecha_registro or _ahora_iso()

    # --- Autenticación ---
    def verificar_password(self, password: str) -> bool:
        return self.password_hash == hash_password(password)

    # --- Acciones del usuario (antes en Cliente) ---
    def registrar_oferta(self, id_carro, monto):
        """Guarda en el historial PERSONAL del usuario que hizo una oferta.
        La validación real de la puja la hace AdministradorCompraVenta.registrar_puja();
        este método solo deja constancia para mostrarla en el perfil / dashboard."""
        oferta = {"id_carro": id_carro, "monto": monto, "estado": "Activa"}
        self.historial_ofertas.append(oferta)
        return oferta

    def agregar_favorito(self, id_carro):
        if id_carro not in self.favoritos:
            self.favoritos.append(id_carro)
            return True
        return False

    def quitar_favorito(self, id_carro):
        if id_carro in self.favoritos:
            self.favoritos.remove(id_carro)
            return True
        return False

    def to_dict(self):
        """Representación segura para mostrar en la UI (sin password_hash)."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "telefono": self.telefono,
            "verificado": self.verificado,
            "reputacion": self.reputacion,
            "autos_en_posesion": list(self.autos_en_posesion),
            "favoritos": list(self.favoritos),
            "ofertas_activas": len([o for o in self.historial_ofertas if o["estado"] == "Activa"]),
        }

    def __str__(self):
        return f"👤 [{self.id}] {self.nombre} ({self.rol.capitalize()}) | Rep: {self.reputacion}⭐"


class Carro:
    """
    Reemplaza a las dos clases Carro que existían antes. Usa los mismos
    nombres de campo que carros.json (incluyendo fecha_inicio / fecha_fin,
    que antes se perdían al cargar los datos).

    estado_subasta ahora puede ser:
      'pendiente_revision' -> recién publicada, esperando que un admin/experto
                               la revise (este es el estado inicial por defecto).
      'activa'              -> aprobada, contando tiempo hasta fecha_fin.
      'vendido' / 'no_vendido' -> ya cerrada.
      'rechazada'           -> un admin la rechazó (ver motivo_rechazo).
    """

    def __init__(self, id_carro, vendedor_id, marca, modelo, anio, kilometraje,
                 precio_base, precio_reserva, estado_subasta="pendiente_revision",
                 fecha_inicio=None, fecha_fin=None, especificaciones=None,
                 extras=None, precio_final_venta=0.0, comprador_id=None,
                 imagen=None, condicion_general=None, descripcion_danos="",
                 documentos_en_regla=False, duracion_dias=7,
                 fecha_publicacion=None, motivo_rechazo=None):
        self.id = id_carro
        self.vendedor_id = vendedor_id
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.kilometraje = kilometraje
        self.precio_base = precio_base
        self.precio_reserva = precio_reserva
        self.estado_subasta = estado_subasta
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.especificaciones = especificaciones if especificaciones is not None else {}
        self.extras = extras if extras is not None else []
        self.precio_final_venta = precio_final_venta
        self.comprador_id = comprador_id
        # --- Imagen del vehículo: puede ser una URL o un string base64 (sin
        # el prefijo 'data:'), ft.Image en Flet acepta ambos en 'src'. ---
        self.imagen = imagen
        # --- Campos para que un admin/experto pueda verificar la subasta ---
        self.condicion_general = condicion_general  # 'Excelente' | 'Buena' | 'Regular' | 'Necesita reparación'
        self.descripcion_danos = descripcion_danos
        self.documentos_en_regla = documentos_en_regla
        self.duracion_dias = duracion_dias  # cuántos días dura la subasta UNA VEZ aprobada
        self.fecha_publicacion = fecha_publicacion or _ahora_iso()
        self.motivo_rechazo = motivo_rechazo

    def tiempo_restante(self):
        """Timedelta hasta fecha_fin, o None si el carro no tiene fecha_fin
        (por ejemplo, mientras está 'pendiente_revision' y todavía no se aprueba)."""
        fin = _parsear_fecha(self.fecha_fin)
        if fin is None:
            return None
        return fin - datetime.now(timezone.utc)

    def esta_vencida(self) -> bool:
        restante = self.tiempo_restante()
        return restante is not None and restante.total_seconds() <= 0

    def to_dict(self):
        restante = self.tiempo_restante()
        return {
            "id": self.id,
            "vendedor_id": self.vendedor_id,
            "marca": self.marca,
            "modelo": self.modelo,
            "anio": self.anio,
            "kilometraje": self.kilometraje,
            "precio_base": self.precio_base,
            "precio_reserva": self.precio_reserva,
            "estado_subasta": self.estado_subasta,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "horas_restantes": round(restante.total_seconds() / 3600, 1) if restante else None,
            "especificaciones": dict(self.especificaciones),
            "extras": list(self.extras),
            "precio_final_venta": self.precio_final_venta,
            "comprador_id": self.comprador_id,
            "imagen": self.imagen,
            "condicion_general": self.condicion_general,
            "descripcion_danos": self.descripcion_danos,
            "documentos_en_regla": self.documentos_en_regla,
            "duracion_dias": self.duracion_dias,
            "fecha_publicacion": self.fecha_publicacion,
            "motivo_rechazo": self.motivo_rechazo,
        }

    def __str__(self):
        return (f"🚗 [{self.id}] {self.marca} {self.modelo} ({self.anio}) | "
                f"Base: ${self.precio_base:,} | Reserva: ${self.precio_reserva:,} "
                f"[{self.estado_subasta.upper()}]")


class Puja:
    def __init__(self, id_puja, id_carro, id_usuario, monto, fecha_hora, pago_verificado):
        self.id = id_puja
        self.id_carro = id_carro
        self.id_usuario = id_usuario
        self.monto = monto
        self.fecha_hora = fecha_hora
        self.pago_verificado = pago_verificado

    def to_dict(self):
        return {
            "id": self.id,
            "id_carro": self.id_carro,
            "id_usuario": self.id_usuario,
            "monto": self.monto,
            "fecha_hora": self.fecha_hora,
            "pago_verificado": self.pago_verificado,
        }
