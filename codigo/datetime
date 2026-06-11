import datetime

class Cliente:
    def __init__(self, ci, nombre, apellido, correo, telefono):
        self.ci = ci  # Cédula de Identidad (Identificador único)
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.telefono = telefono
        self.historial_pujas = []  # Almacenará objetos de la clase Puja

    def registrar_puja(self, puja):
        """Agrega una puja realizada por el cliente a su historial."""
        self.historial_pujas.append(puja)

    def obtener_perfil(self):
        """Retorna la información formateada del cliente."""
        return f"{self.nombre} {self.apellido} (C.I.: {self.ci}) - Correo: {self.correo}"


class Puja:
    def __init__(self, cliente, monto):
        self.cliente = cliente          # Objeto de la clase Cliente que realiza la puja
        self.monto = monto              # Cantidad de dinero ofertada
        self.fecha_hora = datetime.datetime.now() # Momento exacto de la puja

    def __str__(self):
        return f"Puja de ${self.monto} por {self.cliente.nombre} {self.cliente.apellido} a las {self.fecha_hora.strftime('%H:%M:%S')}"


class Subasta:
    def __init__(self, id_subasta, carro, precio_base):
        self.id_subasta = id_subasta
        self.carro = carro              # Descripción o modelo del carro
        self.precio_base = precio_base
        self.activa = True
        self.lista_pujas = []           # Lista que almacena objetos de la clase Puja

    def recibir_puja(self, cliente, monto):
        """
        Permite a un cliente realizar una puja. 
        Valida que sea mayor al precio base y a la puja más alta actual.
        """
        if not self.activa:
            print("Error: Esta subasta ya está cerrada.")
            return False

        # Determinar el monto mínimo requerido
        monto_actual_mas_alto = self.precio_base
        if self.lista_pujas:
            monto_actual_mas_alto = self.lista_pujas[-1].monto

        if monto <= monto_actual_mas_alto:
            print(f"Error: El monto debe ser mayor a la puja actual (${monto_actual_mas_alto}).")
            return False

        # Si la puja es válida, se crea el objeto Puja
        nueva_puja = Puja(cliente, monto)
        
        # Se registra tanto en la subasta como en el historial del cliente
        self.lista_pujas.append(nueva_puja)
        cliente.registrar_puja(nueva_puja)
        
        print(f"¡Puja aceptada con éxito para el carro {self.carro}!")
        return True

    def obtener_ganador(self):
        """Retorna la puja más alta (la última de la lista) si existen pujas."""
        if not self.lista_pujas:
            return None
        return self.lista_pujas[-1]

    def cerrar_subasta(self):
        self.activa = False
        print(f"La subasta del {self.carro} ha sido cerrada.")