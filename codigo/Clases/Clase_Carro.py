class Carro:
    def __init__(self, id_carro, marca, modelo, ano, precio_base):
        self.id_carro = id_carro
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.precio_base = precio_base


class Cliente:
    def __init__(self, cedula, nombre, correo, telefono):
        # Atributos encapsulados (privados)
        self.__cedula = cedula
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        # Historiales del cliente
        self.historial_ofertas = []  # Registro de ofertas realizadas
        self.carritos_favoritos = [] # Lista de carros en la mira

    # --- GETTERS Y SETTERS (Para proteger la C.I.) ---
    @property
    def cedula(self):
        return self.__cedula

    # --- MÉTODOS DE ACCIÓN ---
    def registrar_oferta(self, id_subasta, id_carro, monto):
        """Permite al cliente realizar una oferta por un vehículo."""
        oferta = {
            "id_subasta": id_subasta,
            "id_carro": id_carro,
            "monto": monto,
            "estado": "Activa"  # Puede cambiar a 'Ganada' o 'Superada'
        }
        self.historial_ofertas.append(oferta)
        print(f" Tarjeta de Oferta: {self.nombre} ha ofertado ${monto} por el carro ID {id_carro}.")
        return oferta

    def agregar_favorito(self, carro):
        """Añade un carro a la lista de seguimiento del cliente."""
        if carro not in self.carritos_favoritos:
            self.carritos_favoritos.append(carro)
            print(f"✨ {carro.marca} {carro.modelo} añadido a los favoritos de {self.nombre}.")
        else:
            print("Este carro ya está en tu lista de favoritos.")

    def ver_perfil(self):
        """Muestra la información general del cliente."""
        print(f"\n=== PERFIL DE CLIENTE ===")
        print(f"Nombre: {self.nombre}")
        print(f"C.I.: {self.__cedula}")
        print(f"Correo: {self.correo}")
        print(f"Teléfono: {self.telefono}")
        print(f"Ofertas realizadas: {len(self.historial_ofertas)}")
        print(f"Carros en seguimiento: {len(self.carritos_favoritos)}")
        print("=========================")


if __name__ == "__main__":
    # 1. Creamos un cliente
    cliente1 = Cliente(
        cedula="V-24555666", 
        nombre="Carlos Mendoza", 
        correo="carlos.mendoza@email.com", 
        telefono="0412-5555555"
    )

    # 2. Creamos un par de carros disponibles en la subasta
    carro1 = Carro(101, "Toyota", "Supra MK4", 1998, 45000)
    carro2 = Carro(102, "Nissan", "Skyline R34", 2002, 60000)

    # 3. El cliente interactúa con el sistema
    cliente1.ver_perfil()
    
    # Agrega un carro a favoritos
    cliente1.agregar_favorito(carro1)
    
    # El cliente decide ofertar en una subasta (Subasta ID: #001)
    cliente1.registrar_oferta(id_subasta="SUB-001", id_carro=carro1.id_carro, monto=47000)

    # 4. Volvemos a ver el perfil actualizado
    cliente1.ver_perfil()