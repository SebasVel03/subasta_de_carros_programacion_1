"""
Lógica de negocio central de la app de subastas.

Esta es la versión unificada y corregida de admin.py:
- Arregla el bug de self.comi_porcentaje (ver historial de la conversación).
- Ya no pierde fecha_inicio / fecha_fin al cargar carros.json.
- Agrega registro/login de usuarios, registrar_puja() con validaciones reales,
  cierre automático de subastas vencidas, persistencia a disco, y un set de
  métodos "obtener_..." pensados para alimentar directamente las vistas de Flet.
"""

import json
from datetime import datetime, timedelta, timezone

from .modelos import Usuario, Carro, Puja, hash_password


class AdministradorCompraVenta:
    def __init__(self, comision_plataforma_porcentaje=0.05):
        self.usuarios = {}
        self.carros = {}
        self.pujas = []
        self.comision_porcentaje = comision_plataforma_porcentaje

    # =====================================================================
    # CARGA / PERSISTENCIA
    # =====================================================================
    def cargar_datos_desde_json(self, json_u, json_c, json_p):
        """Carga el sistema a partir de 3 strings JSON ya leídos."""
        try:
            # 1. Usuarios
            for id_u, d in json.loads(json_u).items():
                password_hash = d.get("password_hash") or hash_password(d.get("contraseña", ""))
                self.usuarios[id_u] = Usuario(
                    id_usuario=id_u,
                    nombre=d["nombre"],
                    email=d["email"],
                    password_hash=password_hash,
                    rol=d["rol"],
                    telefono=d.get("telefono", ""),
                    verificado=d.get("verificado", False),
                    autos_en_posesion=list(d.get("autos_en_posesion", [])),
                    reputacion=d.get("reputacion_estrellas", 0.0),
                    fecha_registro=d.get("fecha_registro"),
                )
            # 2. Carros (ahora SÍ guardamos fecha_inicio / fecha_fin)
            for c in json.loads(json_c):
                id_c = c["coche_id"]
                self.carros[id_c] = Carro(
                    id_carro=id_c,
                    vendedor_id=c["vendedor_id"],
                    marca=c["marca"],
                    modelo=c["modelo"],
                    anio=c["año"],
                    kilometraje=c["kilometraje"],
                    precio_base=c["precio_base"],
                    precio_reserva=c["precio_reserva"],
                    estado_subasta=c.get("estado_subasta", "activa"),
                    fecha_inicio=c.get("fecha_inicio"),
                    fecha_fin=c.get("fecha_fin"),
                    especificaciones=c.get("especificaciones", {}),
                    extras=c.get("caracteristicas_extra", []),
                    precio_final_venta=c.get("precio_final_venta", 0.0),
                    comprador_id=c.get("comprador_id"),
                )
            # 3. Pujas
            for id_carro, lista_pujas in json.loads(json_p).items():
                for p in lista_pujas:
                    self.pujas.append(Puja(
                        p["puja_id"], id_carro, p["usuario_id"], p["monto"],
                        p["fecha_hora"], p["metodo_pago_verificado"],
                    ))
            return True
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")
            return False

    def cargar_datos_desde_archivos(self, ruta_usuarios, ruta_carros, ruta_pujas):
        """Lee los 3 .json desde disco (UTF-8, por los acentos/ñ) y carga el sistema."""
        with open(ruta_usuarios, encoding="utf-8") as f:
            txt_u = f.read()
        with open(ruta_carros, encoding="utf-8") as f:
            txt_c = f.read()
        with open(ruta_pujas, encoding="utf-8") as f:
            txt_p = f.read()
        return self.cargar_datos_desde_json(txt_u, txt_c, txt_p)

    def guardar_datos_a_archivos(self, ruta_usuarios, ruta_carros, ruta_pujas):
        """
        Persiste el estado actual de vuelta a disco.

        IMPORTANTE: a partir de aquí los usuarios se guardan con "password_hash"
        en vez de "contraseña" en texto plano. cargar_datos_desde_json() ya
        soporta ambos formatos (ver arriba), así que la migración es transparente.
        """
        usuarios_json = {
            u.id: {
                "nombre": u.nombre,
                "email": u.email,
                "password_hash": u.password_hash,
                "telefono": u.telefono,
                "rol": u.rol,
                "fecha_registro": u.fecha_registro,
                "reputacion_estrellas": u.reputacion,
                "verificado": u.verificado,
                "autos_en_posesion": u.autos_en_posesion,
            }
            for u in self.usuarios.values()
        }
        carros_json = [
            {
                "coche_id": c.id,
                "vendedor_id": c.vendedor_id,
                "marca": c.marca,
                "modelo": c.modelo,
                "año": c.anio,
                "kilometraje": c.kilometraje,
                "precio_base": c.precio_base,
                "precio_reserva": c.precio_reserva,
                "estado_subasta": c.estado_subasta,
                "fecha_inicio": c.fecha_inicio,
                "fecha_fin": c.fecha_fin,
                "especificaciones": c.especificaciones,
                "caracteristicas_extra": c.extras,
                "precio_final_venta": c.precio_final_venta,
                "comprador_id": c.comprador_id,
            }
            for c in self.carros.values()
        ]
        pujas_json = {}
        for p in self.pujas:
            pujas_json.setdefault(p.id_carro, []).append({
                "puja_id": p.id,
                "usuario_id": p.id_usuario,
                "monto": p.monto,
                "fecha_hora": p.fecha_hora,
                "metodo_pago_verificado": p.pago_verificado,
            })

        with open(ruta_usuarios, "w", encoding="utf-8") as f:
            json.dump(usuarios_json, f, ensure_ascii=False, indent=2)
        with open(ruta_carros, "w", encoding="utf-8") as f:
            json.dump(carros_json, f, ensure_ascii=False, indent=2)
        with open(ruta_pujas, "w", encoding="utf-8") as f:
            json.dump(pujas_json, f, ensure_ascii=False, indent=2)

    # =====================================================================
    # AUTENTICACIÓN
    # =====================================================================
    def registrar_usuario(self, nombre, email, password, rol="postor", telefono=""):
        if any(u.email.lower() == email.lower() for u in self.usuarios.values()):
            return False, "Ya existe una cuenta con ese correo."

        nuevo_id = f"usr_{len(self.usuarios) + 1:03d}"
        nuevo_usuario = Usuario(
            id_usuario=nuevo_id,
            nombre=nombre,
            email=email,
            password_hash=hash_password(password),
            rol=rol,
            telefono=telefono,
            # TODO: reemplazar por un flujo real de verificación (confirmación
            # de correo, revisión manual de documentos, etc.). Por ahora se
            # autoverifica al registrarse para que el equipo pueda probar
            # pujar/publicar de inmediato sin quedar bloqueado.
            verificado=True,
        )
        self.usuarios[nuevo_id] = nuevo_usuario
        return True, nuevo_usuario

    def autenticar_usuario(self, email, password):
        for usuario in self.usuarios.values():
            if usuario.email.lower() == email.lower():
                if usuario.verificar_password(password):
                    return True, usuario
                return False, "Contraseña incorrecta."
        return False, "No existe una cuenta con ese correo."

    # =====================================================================
    # MÓDULO COMPRA (publicar un carro)
    # =====================================================================
    def recibir_carro_compra(self, id_vendedor, coche_id, marca, modelo, anio, kilometraje,
                              precio_base, precio_reserva, especificaciones, extras,
                              fecha_inicio=None, fecha_fin=None):
        vendedor = self.usuarios.get(id_vendedor)
        if not vendedor or vendedor.rol != "vendedor":
            return False, f"El usuario {id_vendedor} no existe o no tiene rol de vendedor."
        if not vendedor.verificado:
            return False, f"El vendedor {vendedor.nombre} no está verificado. No puede publicar autos."
        if coche_id in self.carros:
            return False, f"Ya existe un carro publicado con el id {coche_id}."

        nuevo_carro = Carro(
            coche_id, id_vendedor, marca, modelo, anio, kilometraje, precio_base,
            precio_reserva, "activa", fecha_inicio, fecha_fin, especificaciones, extras,
        )
        self.carros[coche_id] = nuevo_carro
        vendedor.autos_en_posesion.append(coche_id)
        return True, nuevo_carro

    # =====================================================================
    # MÓDULO PUJAS (antes no existía: las pujas se insertaban a mano)
    # =====================================================================
    def registrar_puja(self, id_usuario, id_carro, monto, metodo_pago_verificado=True):
        usuario = self.usuarios.get(id_usuario)
        carro = self.carros.get(id_carro)

        if not usuario:
            return False, "El usuario no existe."
        if not carro:
            return False, "El carro no existe."
        if carro.estado_subasta != "activa" or carro.esta_vencida():
            return False, f"La subasta de {carro.marca} {carro.modelo} ya no está activa."
        if not usuario.verificado:
            return False, "Debes verificar tu cuenta antes de poder pujar."
        if usuario.id == carro.vendedor_id:
            return False, "No puedes pujar por tu propio vehículo."

        pujas_validas = [p for p in self.pujas if p.id_carro == id_carro and p.pago_verificado]
        monto_minimo = max([carro.precio_base] + [p.monto for p in pujas_validas])
        if monto <= monto_minimo:
            return False, f"La puja debe ser mayor a ${monto_minimo:,}."

        nueva_puja = Puja(
            id_puja=f"puj_{id_carro}_{len(self.pujas) + 1:03d}",
            id_carro=id_carro,
            id_usuario=id_usuario,
            monto=monto,
            fecha_hora=datetime.now(timezone.utc).isoformat(),
            pago_verificado=metodo_pago_verificado,
        )
        self.pujas.append(nueva_puja)
        usuario.registrar_oferta(id_carro=id_carro, monto=monto)

        # Las pujas anteriores de este mismo carro quedan "Superada"
        for p in pujas_validas:
            otro = self.usuarios.get(p.id_usuario)
            if not otro:
                continue
            for oferta in otro.historial_ofertas:
                if oferta["id_carro"] == id_carro and oferta["estado"] == "Activa":
                    oferta["estado"] = "Superada"

        return True, nueva_puja

    # =====================================================================
    # MÓDULO VENTA (cierre de subastas)
    # =====================================================================
    def cerrar_venta_subasta(self, id_carro):
        carro = self.carros.get(id_carro)
        if not carro:
            return False, "El carro no existe."
        if carro.estado_subasta != "activa":
            return False, f"El carro ya no está activo (estado actual: {carro.estado_subasta})."

        pujas_carro = [p for p in self.pujas if p.id_carro == id_carro and p.pago_verificado]

        if not pujas_carro:
            carro.estado_subasta = "no_vendido"
            return True, None

        pujas_carro.sort(key=lambda x: x.monto, reverse=True)
        mejor_puja = pujas_carro[0]

        if mejor_puja.monto < carro.precio_reserva:
            carro.estado_subasta = "no_vendido"
            return True, None

        carro.estado_subasta = "vendido"
        carro.precio_final_venta = mejor_puja.monto
        carro.comprador_id = mejor_puja.id_usuario

        vendedor = self.usuarios.get(carro.vendedor_id)
        comprador = self.usuarios.get(mejor_puja.id_usuario)
        if vendedor and id_carro in vendedor.autos_en_posesion:
            vendedor.autos_en_posesion.remove(id_carro)
        if comprador:
            comprador.autos_en_posesion.append(id_carro)

        # Actualiza el historial personal de cada postor: Ganada / Perdida
        for p in pujas_carro:
            postor = self.usuarios.get(p.id_usuario)
            if not postor:
                continue
            for oferta in postor.historial_ofertas:
                if oferta["id_carro"] == id_carro:
                    oferta["estado"] = "Ganada" if p.id_usuario == mejor_puja.id_usuario else "Perdida"

        return True, carro

    def cerrar_subastas_vencidas(self):
        """Recorre todos los carros activos y cierra los que ya pasaron su fecha_fin.
        Esto antes no existía: el cierre era 100% manual."""
        cerrados = []
        for carro in list(self.carros.values()):
            if carro.estado_subasta == "activa" and carro.esta_vencida():
                self.cerrar_venta_subasta(carro.id)
                cerrados.append(carro.id)
        return cerrados

    # =====================================================================
    # PUBLICACIÓN simplificada (lo que usa la pantalla "Mis Carros")
    # =====================================================================
    def publicar_carro(self, id_vendedor, marca, modelo, anio, kilometraje,
                        precio_base, precio_reserva, dias_duracion=7,
                        especificaciones=None, extras=None):
        """
        Wrapper sobre recibir_carro_compra() que genera el id y las fechas
        automáticamente, para que la pantalla de publicación solo tenga que
        pedir los campos que el usuario realmente puede llenar.
        """
        coche_id = f"auto_{len(self.carros) + 1:03d}"
        ahora = datetime.now(timezone.utc)
        fecha_inicio = ahora.isoformat()
        fecha_fin = (ahora + timedelta(days=dias_duracion)).isoformat()

        return self.recibir_carro_compra(
            id_vendedor=id_vendedor, coche_id=coche_id, marca=marca, modelo=modelo,
            anio=anio, kilometraje=kilometraje, precio_base=precio_base,
            precio_reserva=precio_reserva, especificaciones=especificaciones or {},
            extras=extras or [], fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        )

    # =====================================================================
    # CONSULTAS PARA LAS PESTAÑAS DEL FRONT END
    # =====================================================================
    def obtener_puja_maxima(self, id_carro):
        """Monto más alto pujado por un carro (o su precio_base si no hay pujas)."""
        carro = self.carros.get(id_carro)
        if not carro:
            return 0
        pujas_validas = [p.monto for p in self.pujas if p.id_carro == id_carro and p.pago_verificado]
        return max([carro.precio_base] + pujas_validas)

    def obtener_mis_carros(self, id_usuario):
        """Pestaña 'MIS CARROS': todo lo que este usuario ha publicado, sea cual sea su estado."""
        mios = [c for c in self.carros.values() if c.vendedor_id == id_usuario]
        mios.sort(key=lambda c: (c.estado_subasta != "activa", c.fecha_fin or ""))
        resultado = []
        for c in mios:
            d = c.to_dict()
            d["puja_maxima"] = self.obtener_puja_maxima(c.id)
            d["num_pujas"] = len([p for p in self.pujas if p.id_carro == c.id])
            resultado.append(d)
        return resultado

    def obtener_subastas_explorar(self, id_usuario=None):
        """Pestaña 'EXPLORAR SUBASTAS': todas las subastas activas de la plataforma."""
        activos = [c for c in self.carros.values() if c.estado_subasta == "activa"]
        activos.sort(key=lambda c: c.tiempo_restante() or 0)
        resultado = []
        for c in activos:
            d = c.to_dict()
            d["puja_maxima"] = self.obtener_puja_maxima(c.id)
            d["num_pujas"] = len([p for p in self.pujas if p.id_carro == c.id])
            d["es_propio"] = (c.vendedor_id == id_usuario) if id_usuario else False
            resultado.append(d)
        return resultado

    def obtener_mis_subastas_activas(self, id_usuario):
        """
        Pestaña 'SUBASTAS ACTIVAS': subastas activas en las que este usuario
        participa (tiene una puja o la marcó como favorita). Es justo la
        diferencia con 'Explorar Subastas', que muestra TODO el mercado.
        """
        usuario = self.usuarios.get(id_usuario)
        ids_con_oferta = {o["id_carro"] for o in (usuario.historial_ofertas if usuario else [])}
        ids_favoritos = set(usuario.favoritos) if usuario else set()
        ids_interes = ids_con_oferta | ids_favoritos

        activos = [c for c in self.carros.values()
                   if c.estado_subasta == "activa" and c.id in ids_interes]
        activos.sort(key=lambda c: c.tiempo_restante() or 0)

        resultado = []
        for c in activos:
            mi_oferta = next((o for o in usuario.historial_ofertas if o["id_carro"] == c.id), None)
            d = c.to_dict()
            d["puja_maxima"] = self.obtener_puja_maxima(c.id)
            d["mi_estado"] = mi_oferta["estado"] if mi_oferta else "Solo en favoritos"
            d["mi_monto"] = mi_oferta["monto"] if mi_oferta else None
            resultado.append(d)
        return resultado

    def obtener_mis_ventas(self, id_usuario):
        """Pestaña 'VENTAS': historial de subastas YA CERRADAS de este vendedor."""
        cerradas = [c for c in self.carros.values()
                    if c.vendedor_id == id_usuario and c.estado_subasta in ("vendido", "no_vendido")]
        cerradas.sort(key=lambda c: c.fecha_fin or "", reverse=True)

        resultado = []
        for c in cerradas:
            comprador = self.usuarios.get(c.comprador_id) if c.comprador_id else None
            d = c.to_dict()
            d["comprador_nombre"] = comprador.nombre if comprador else None
            d["comision"] = c.precio_final_venta * self.comision_porcentaje if c.estado_subasta == "vendido" else 0
            resultado.append(d)
        return resultado

    # =====================================================================
    # MÉTRICAS / REPORTES (pensados para alimentar el dashboard de Flet)
    # =====================================================================
    def calcular_resumen_financiero(self):
        vendidos = [c for c in self.carros.values() if c.estado_subasta == "vendido"]
        total_ventas = sum(c.precio_final_venta for c in vendidos)
        ganancia_plataforma = total_ventas * self.comision_porcentaje
        return {
            "autos_catalogo": len(self.carros),
            "autos_vendidos": len(vendidos),
            "volumen_total": total_ventas,
            "comision_porcentaje": self.comision_porcentaje,
            "ganancia_plataforma": ganancia_plataforma,
        }

    def generar_reporte_financiero(self):
        """Versión CLI del reporte (se mantiene por compatibilidad con admin.py original)."""
        r = self.calcular_resumen_financiero()
        print("\n==================================================")
        print("    REPORTE FINANCIERO DE COMPRA Y VENTA (ADMIN)   ")
        print("==================================================")
        print(f" Autos en catálogo total:     {r['autos_catalogo']}")
        print(f" Autos vendidos con éxito:   {r['autos_vendidos']}")
        print(f" Volumen Total Transaccionado: ${r['volumen_total']:,.2f}")
        print(f" Comisión de Plataforma ({r['comision_porcentaje']*100}%): ${r['ganancia_plataforma']:,.2f}")
        print("==================================================\n")

    def obtener_resumen_dashboard(self, id_usuario):
        """
        Números para las 3 tarjetas superiores del dashboard (RESUMEN), vistas
        desde la perspectiva de un usuario específico.

        Definiciones (decisión de producto, ajustar si el equipo define otra cosa):
        - ganancias: suma de precio_final_venta de los autos que este usuario VENDIÓ.
        - gastado: suma de precio_final_venta de los autos que este usuario COMPRÓ.
        - subastas_activas_pendientes: subastas activas en TODA la plataforma
          (no solo las del usuario), igual que se ve en la referencia de diseño.
        """
        vendidos_por_el = [c for c in self.carros.values()
                            if c.vendedor_id == id_usuario and c.estado_subasta == "vendido"]
        comprados_por_el = [c for c in self.carros.values()
                             if c.comprador_id == id_usuario and c.estado_subasta == "vendido"]
        activas = [c for c in self.carros.values() if c.estado_subasta == "activa"]

        return {
            "ganancias": sum(c.precio_final_venta for c in vendidos_por_el),
            "gastado": sum(c.precio_final_venta for c in comprados_por_el),
            "subastas_activas_pendientes": len(activas),
        }

    def obtener_subastadores_frecuentes(self, top_n=5):
        """Usuarios que más pujas han hecho en toda la plataforma."""
        conteo = {}
        for p in self.pujas:
            conteo[p.id_usuario] = conteo.get(p.id_usuario, 0) + 1

        ranking = sorted(conteo.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
        resultado = []
        for id_usuario, cantidad in ranking:
            usuario = self.usuarios.get(id_usuario)
            if usuario:
                resultado.append({
                    "nombre": usuario.nombre,
                    "email": usuario.email,
                    "cantidad_pujas": cantidad,
                })
        return resultado

    def obtener_subastas_por_cerrar(self, top_n=5):
        """
        Reemplaza a la tarjeta 'TASAS DE CAMBIO' del mockup (esa era contenido
        de plantilla de Figma, no tiene relación con el negocio). Esta sí es
        información real y útil: las subastas activas más próximas a cerrar.
        """
        activas = [c for c in self.carros.values()
                   if c.estado_subasta == "activa" and c.tiempo_restante() is not None]
        activas.sort(key=lambda c: c.tiempo_restante())

        resultado = []
        for carro in activas[:top_n]:
            num_pujas = len([p for p in self.pujas if p.id_carro == carro.id])
            horas = carro.tiempo_restante().total_seconds() / 3600
            resultado.append({
                "carro": f"{carro.marca} {carro.modelo}",
                "num_pujas": num_pujas,
                "horas_restantes": round(horas, 1),
            })
        return resultado

    def obtener_ingresos_mensuales(self):
        """
        Agrega precio_final_venta por mes a partir de las ventas reales.

        NOTA: con la cantidad de datos de ejemplo que hay ahora (1-2 ventas),
        esto va a devolver muy pocos puntos. Es el comportamiento correcto:
        el gráfico de ingresos del dashboard se va a ver disperso hasta que
        haya más historial real de ventas. No hay que rellenarlo con datos
        inventados.
        """
        por_mes = {}
        for c in self.carros.values():
            if c.estado_subasta == "vendido" and c.fecha_fin:
                mes = c.fecha_fin[:7]  # 'YYYY-MM'
                por_mes[mes] = por_mes.get(mes, 0) + c.precio_final_venta
        return dict(sorted(por_mes.items()))

    def obtener_actividad_pujas_mensual(self):
        """
        Cantidad de pujas por mes (toda la plataforma). Es la métrica que
        alimenta 'MOVIMIENTOS NETOS' en el dashboard: una cosa distinta al
        volumen de ventas, para no graficar dos veces el mismo número.
        Mismo aviso que en obtener_ingresos_mensuales(): con pocos datos de
        ejemplo, va a haber pocos puntos. Es esperado.
        """
        por_mes = {}
        for p in self.pujas:
            if p.fecha_hora:
                mes = p.fecha_hora[:7]
                por_mes[mes] = por_mes.get(mes, 0) + 1
        return dict(sorted(por_mes.items()))
