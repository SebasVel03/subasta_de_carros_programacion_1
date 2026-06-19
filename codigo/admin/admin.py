import json
from datetime import datetime

class Usuario:
    def __init__(self, id_usuario, nombre, email, rol, verificado, autos_en_posesion, reputacion):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.rol = rol  # 'vendedor' o 'postor'
        self.verificado = verificado
        self.autos_en_posesion = autos_en_posesion
        self.reputacion = reputacion

    def __str__(self):
        return f"👤 [{self.id}] {self.nombre} ({self.rol.capitalize()}) | Rep: {self.reputacion}⭐"


class Carro:
    def __init__(self, id_carro, vendedor_id, marca, modelo, anio, kilometraje, precio_base, precio_reserva, estado_subasta, especificaciones, extras):
        self.id = id_carro
        self.vendedor_id = vendedor_id
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.kilometraje = kilometraje
        self.precio_base = precio_base
        self.precio_reserva = precio_reserva
        self.estado_subasta = estado_subasta  # 'activa', 'vendido', 'no_vendido'
        self.especificaciones = especificaciones
        self.extras = extras
        self.precio_final_venta = 0.0
        self.comprador_id = None

    def __str__(self):
        return f"🚗 [{self.id}] {self.marca} {self.modelo} ({self.anio}) | Base: ${self.precio_base:,} | Reserva: ${self.precio_reserva:,} [{self.estado_subasta.upper()}]"


class Puja:
    def __init__(self, id_puja, id_carro, id_usuario, monto, fecha_hora, pago_verificado):
        self.id = id_puja
        self.id_carro = id_carro
        self.id_usuario = id_usuario
        self.monto = monto
        self.fecha_hora = fecha_hora
        self.pago_verificado = pago_verificado


class AdministradorCompraVenta:
    def __init__(self, comision_plataforma_porcentaje=0.05):
        self.usuarios = {}
        self.carros = {}
        self.pujas = []
        self.comision_porcentaje = comision_plataforma_porcentaje  # 5% de comisión por venta

    def cargar_datos_desde_json(self, json_u, json_c, json_p):
        """Carga inicial del sistema con las 3 estructuras de datos entregadas."""
        try:
            # 1. Usuarios
            for id_u, d in json.loads(json_u).items():
                self.usuarios[id_u] = Usuario(id_u, d["nombre"], d["email"], d["rol"], d["verificado"], d["autos_en_posesion"], d["reputacion_estrellas"])
            # 2. Carros
            for c in json.loads(json_c):
                id_c = c["coche_id"]
                self.carros[id_c] = Carro(id_c, c["vendedor_id"], c["marca"], c["modelo"], c["año"], c["kilometraje"], c["precio_base"], c["precio_reserva"], c["estado_subasta"], c["especificaciones"], c["caracteristicas_extra"])
            # 3. Pujas
            for id_carro, lista_pujas in json.loads(json_p).items():
                for p in lista_pujas:
                    self.pujas.append(Puja(p["puja_id"], id_carro, p["usuario_id"], p["monto"], p["fecha_hora"], p["metodo_pago_verificado"]))
            print("✔️ [Sistema] Datos cargados e indexados correctamente.")
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")

    def recibir_carro_compra(self, id_vendedor, coche_id, marca, modelo, anio, kilometraje, precio_base, precio_reserva, especificaciones, extras):
        """MÓDULO COMPRA: El administrador acepta un coche de un vendedor verificado y lo añade al mercado."""
        vendedor = self.usuarios.get(id_vendedor)
        
        if not vendedor or vendedor.rol != "vendedor":
            print(f"❌ Error: El usuario {id_vendedor} no existe o no tiene rol de vendedor.")
            return
        if not vendedor.verificado:
            print(f"⚠️ Alerta: El vendedor {vendedor.nombre} no está verificado. No puede publicar autos.")
            return

        nuevo_carro = Carro(coche_id, id_vendedor, marca, modelo, anio, kilometraje, precio_base, precio_reserva, "activa", especificaciones, extras)
        self.carros[coche_id] = nuevo_carro
        vendedor.autos_en_posesion.append(coche_id)
        print(f"📥 [Compra/Publicación] Coche {marca} {modelo} [{coche_id}] recibido del vendedor {vendedor.nombre} y puesto en subasta.")

    def cerrar_venta_subasta(self, id_carro):
        """MÓDULO VENTA: Cierra la subasta, evalúa la puja más alta y procesa la venta."""
        carro = self.carros.get(id_carro)
        if not carro:
            print(f"❌ El carro {id_carro} no existe.")
            return
        if carro.estado_subasta != "activa":
            print(f"⚠️ El carro {id_carro} ya no está activo (Estado actual: {carro.estado_subasta}).")
            return

        # Buscar todas las pujas de este carro
        pujas_carro = [p for p in self.pujas if p.id_carro == id_carro and p.pago_verificado]
        
        if not pujas_carro:
            carro.estado_subasta = "no_vendido"
            print(f"🛑 Subasta Cerrada: El {carro.marca} {carro.modelo} no recibió pujas válidas.")
            return

        # Obtener la puja más alta
        pujas_carro.sort(key=lambda x: x.monto, reverse=True)
        mejor_puja = pujas_carro[0]

        # Validar Precio de Reserva
        if mejor_puja.monto < carro.precio_reserva:
            carro.estado_subasta = "no_vendido"
            print(f"🛑 Subasta Cerrada: La oferta más alta (${mejor_puja.monto:,}) no alcanzó el precio de reserva (${carro.precio_reserva:,}). No se vende.")
        else:
            # Procesar la Venta exitosa
            carro.estado_subasta = "vendido"
            carro.precio_final_venta = mejor_puja.monto
            carro.comprador_id = mejor_puja.id_usuario
            
            # Transferencia de posesión conceptual
            vendedor = self.usuarios[carro.vendedor_id]
            comprador = self.usuarios[mejor_puja.id_usuario]
            
            if id_carro in vendedor.autos_en_posesion:
                vendedor.autos_en_posesion.remove(id_carro)
            comprador.autos_en_posesion.append(id_carro)
            
            print(f"🤝 [Venta Exitosa] ¡{carro.marca} {carro.modelo} VENDIDO! Comprador: {comprador.nombre} por ${carro.precio_final_venta:,}")

    def generar_reporte_financiero(self):
        """Calcula el volumen del mercado y las ganancias por comisiones de la app."""
        total_ventas = sum(c.precio_final_venta for c in self.carros.values() if c.estado_subasta == "vendido")
        ganancia_plataforma = total_ventas * self.comiporcentaje_actual() # aplicando tasa fija
        ganancia_plataforma = total_ventas * self.comision_porcentaje

        print("\n==================================================")
        print("    REPORTE FINANCIERO DE COMPRA Y VENTA (ADMIN)   ")
        print("==================================================")
        print(f" Autos en catálogo total:     {len(self.carros)}")
        print(f" Autos vendidos con éxito:   {len([c for c in self.carros.values() if c.estado_subasta == 'vendido'])}")
        print(f" Volumen Total Transaccionado: ${total_ventas:,.2f}")
        print(f" Comisión de Plataforma ({self.comision_porcentaje*100}%): ${ganancia_plataforma:,.2f}")
        print("==================================================\n")


# =====================================================================
# EJECUCIÓN CON TUS JSON INTEGRADOS
# =====================================================================
if __name__ == "__main__":
    
    # Tus 3 estructuras JSON reales
    json_usuarios = '{"usr_001": {"nombre": "Ana Lepage", "email": "ana.lepage@email.com", "contraseña": "contraseña1212", "telefono": "+34600111222", "rol": "vendedor", "fecha_registro": "2026-01-15T09:30:00Z", "reputacion_estrellas": 4.8, "verificado": true, "autos_en_posesion": ["auto_101", "auto_102"]}, "usr_002": {"nombre": "Carlos Mendoza", "email": "carlos.m@email.com", "contraseña": "contraseña1111", "telefono": "+34600333444", "rol": "postor", "fecha_registro": "2026-03-22T14:15:00Z", "reputacion_estrellas": 5.0, "verificado": true, "autos_en_posesion": []}, "usr_003": {"nombre": "María Silva", "email": "maria.silva@email.com", "contraseña": "contraseña1313", "telefono": "+34600555666", "rol": "postor", "fecha_registro": "2026-05-01T18:45:00Z", "reputacion_estrellas": 4.2, "verificado": false, "autos_en_posesion": []}}'
    
    json_carros = '[{"coche_id": "auto_101", "vendedor_id": "usr_001", "marca": "Toyota", "modelo": "Corolla", "año": 2022, "kilometraje": 35000, "precio_base": 18000, "precio_reserva": 19500, "estado_subasta": "activa", "fecha_inicio": "2026-06-10T08:00:00Z", "fecha_fin": "2026-06-17T20:00:00Z", "especificaciones": {"motor": "1.8L Híbrido", "transmision": "Automática e-CVT", "combustible": "Híbrido", "color": "Gris Plata"}, "caracteristicas_extra": ["asientos de cuero", "cámara de retroceso", "control de crucero adaptativo"]}, {"coche_id": "auto_102", "vendedor_id": "usr_001", "marca": "Ford", "modelo": "Mustang GT", "año": 2020, "kilometraje": 18000, "precio_base": 35000, "precio_reserva": 38000, "estado_subasta": "activa", "fecha_inicio": "2026-06-11T00:00:00Z", "fecha_fin": "2026-06-18T00:00:00Z", "especificaciones": {"motor": "5.0V8", "transmision": "Manual", "combustible": "Gasolina", "color": "Negro Shadow"}, "caracteristicas_extra": ["escape activo de rendimiento", "frenos Brembo", "asientos deportivos Recaro"]}]'
    
    json_pujas = '{"auto_101": [{"puja_id": "puj_101_001", "usuario_id": "usr_002", "monto": 18500, "fecha_hora": "2026-06-11T09:15:00Z", "metodo_pago_verificado": true}, {"puja_id": "puj_101_002", "usuario_id": "usr_003", "monto": 19200, "fecha_hora": "2026-06-11T10:30:22Z", "metodo_pago_verificado": true}], "auto_102": []}'

    # Instanciamos el manager
    modulo_admin = AdministradorCompraVenta()
    modulo_admin.cargar_datos_desde_json(json_usuarios, json_carros, json_pujas)

    print("\n--- 🛠️ SIMULANDO PROCESO DE COMPRE (Añadir nuevo coche al inventario) ---")
    modulo_admin.recibir_carro_compra(
        id_vendedor="usr_001", coche_id="auto_103", marca="Audi", modelo="A4", anio=2021, kilometraje=40000,
        precio_base=22000, precio_reserva=24000, 
        especificaciones={"motor": "2.0 TFSI", "transmision": "S-tronic", "color": "Azul"}, extras=["Techo solar"]
    )

    print("\n--- 🔨 SIMULANDO PROCESO DE VENTA (Cierre de subastas basado en tus pujas) ---")
    # Caso 1: El auto_101 tiene puja máxima de 19200, pero su reserva es 19500. No se debería vender.
    modulo_admin.cerrar_venta_subasta("auto_101")
    
    # Para ver una venta exitosa, simulemos que entra una puja de Carlos (usr_002) que sí rompe la reserva del Corolla:
    modulo_admin.pujas.append(Puja("puj_101_003", "auto_101", "usr_002", 21000, "2026-06-19T10:00:00Z", True))
    
    # Reiniciamos el estado para el ejemplo y cerramos ahora que sí hay una puja alta
    modulo_admin.carros["auto_101"].estado_subasta = "activa"
    modulo_admin.cerrar_venta_subasta("auto_101")

    print("\n--- 📊 BALANCE DE OPERACIONES ---")
    modulo_admin.generar_reporte_financiero()