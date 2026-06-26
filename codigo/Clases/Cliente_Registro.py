from Clase_Carro import Carro
from Clase_Cliente import Cliente

if __name__ == "__main__":
    # 1. Creamos un cliente (Fíjate que el paréntesis NO se cierra en Cliente)
    cliente1 = Cliente(
        cedula="V-24555666", 
        nombre="Carlos Mendoza", 
        correo="carlos.mendoza@email.com", 
        telefono="0412-5555555"
    ) # <--- El paréntesis se cierra al FINAL de los datos

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