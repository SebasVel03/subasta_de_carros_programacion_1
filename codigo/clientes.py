# subasta_de_carros_programacion_1

# repositorio_clientes funcionará como nuestra base de datos en memoria.
# La clave será la C.I. (Cédula de Identidad) y el valor será un diccionario con los datos del cliente.
repositorio_clientes = {}

def registrar_cliente(ci, nombre, apellido, correo, telefono):
    """
    Registra un nuevo cliente en el sistema.
    Retorna True si se registró con éxito, o False si la C.I. ya existe.
    """
    if ci in repositorio_clientes:
        print(f"Error: El cliente con C.I. {ci} ya está registrado.")
        return False
    
    # Creamos el perfil del cliente utilizando un diccionario
    nuevo_cliente = {
        "nombre": nombre,
        "apellido": apellido,
        "correo": correo,
        "telefono": telefono,
        "historial_pujas": []  # Lista para guardar los carros por los que ha ofertado
    }
    
    repositorio_clientes[ci] = nuevo_cliente
    print(f"¡Cliente {nombre} {apellido} registrado con éxito!")
    return True

def obtener_cliente(ci):
    """
    Busca un cliente por su C.I.
    Retorna el diccionario del cliente si existe, o None si no se encuentra.
    """
    return repositorio_clientes.get(ci, None)

def actualizar_correo(ci, nuevo_correo):
    """
    Actualiza el correo electrónico de un cliente existente.
    """
    cliente = obtener_cliente(ci)
    if cliente:
        cliente["correo"] = nuevo_correo
        return True
    return False

def registrar_puja_cliente(ci, id_carro, monto):
    """
    Registra una oferta/puja en el historial del cliente.
    """
    cliente = obtener_cliente(ci)
    if cliente:
        puja = {"id_carro": id_carro, "monto": monto}
        cliente["historial_pujas"].append(puja)
        return True
    return False