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