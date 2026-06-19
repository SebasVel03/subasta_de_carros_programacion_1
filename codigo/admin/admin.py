import json

class Usuario:
    def __init__(self, id_usuario, nombre, tipo):
        self.id = id_usuario
        self.nombre = nombre
        self.tipo = tipo

    def __str__(self):
        return f"[{self.id}] {self.nombre} ({self.tipo})"


class Carro:
    def __init__(self, id_carro, marca, modelo, anio, precio_base, estado="Disponible"):
        self.id = id_carro
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.precio_base = precio_base
        self.estado = estado

    def __str__(self):
        return f"[{self.id}] {self.marca} {self.modelo} ({self.anio}) - Base: ${self.precio_base} | {self.estado}"


class Puja:
    def __init__(self, id_puja, id_carro, id_usuario, monto):
        self.id = id_puja
        self.id_carro = id_carro
        self.id_usuario = id_usuario
        self.monto = monto

    def __str__(self):
        return f"Puja #{self.id}: Usuario {self.id_usuario} ofreció ${self.monto} por Carro {self.id_carro}"


class AdministradorSubastas:
    def __init__(self):
        self.usuarios = {}
        self.carros = {}
        self.pujas = []

    def cargar_sistema(self, json_u, json_c, json_p):
        """Carga los datos desde tres fuentes JSON independientes (strings)."""
        try:
            # 1. Cargar Usuarios
            usuarios_lista = json.loads(json_u)
            for u in usuarios_lista:
                self.usuarios[u["id"]] = Usuario(u["id"], u["nombre"], u["tipo"])

            # 2. Cargar Carros
            carros_lista = json.loads(json_c)
            for c in carros_lista:
                self.carros[c["id"]] = Carro(c["id"], c["marca"], c["modelo"], c["anio"], c["precio_base"], c["estado"])

            # 3. Cargar Pujas
            pujas_lista = json.loads(json_p)
            for p in pujas_lista:
                self.pujas.append(Puja(p["id"], p["id_carro"], p["id_usuario"], p["monto"]))

            print("✔️ Todos los módulos JSON fueron cargados y vinculados con éxito.")
        except Exception as e:
            print(f"❌ Error al parsear los JSON: {e}")

    def mostrar_tablero(self):
        """Muestra un resumen del estado actual de la plataforma."""
        print("\n" + "="*40)
        print("       PANEL DE ADMINISTRACIÓN        ")
        print("="*40)
        print(f"👥 USUARIOS ({len(self.usuarios)}):")
        for u in self.usuarios.values(): print(f"  {u}")
        
        print(f"\n🚗 CARROS ({len(self.carros)}):")
        for c in self.carros.values(): print(f"  {c}")
        
        print(f"\n🔨 HISTORIAL DE PUJAS ({len(self.pujas)}):")
        for p in self.pujas: print(f"  {p}")
        print("="*40 + "\n")


# =====================================================================
# EJEMPLO DE EJECUCIÓN
# =====================================================================
if __name__ == "__main__":
    
    # Tus 3 fuentes de datos JSON independientes
    json_usuarios = '[{"id": 1, "nombre": "Juan Pérez", "tipo": "comprador"}, {"id": 2, "nombre": "María López", "tipo": "comprador"}]'
    
    json_carros = '[{"id": 10, "marca": "Mazda", "modelo": "3", "anio": 2019, "precio_base": 12000, "estado": "Disponible"}, {"id": 20, "marca": "BMW", "modelo": "M3", "anio": 2021, "precio_base": 45000, "estado": "Disponible"}]'
    
    json_pujas = '[{"id": 901, "id_carro": 10, "id_usuario": 1, "monto": 12500}]'

    # Inicializamos el administrador de la subasta
    subasta_admin = AdministradorSubastas()
    
    # Cargamos las tres fuentes de datos
    subasta_admin.cargar_sistema(json_usuarios, json_carros, json_pujas)
    
    # Mostramos el resultado en el tablero
    subasta_admin.mostrar_tablero()