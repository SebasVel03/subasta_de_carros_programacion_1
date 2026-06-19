import clientes

def menu_principal():
    while True:
        print("\n--- SISTEMA DE SUBASTAS - MÓDULO CLIENTES ---")
        print("1. Registrar nuevo cliente")
        print("2. Buscar cliente por C.I.")
        print("3. Modificar correo de cliente")
        print("4. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            print("\n-- Registro de Cliente --")
            ci = input("C.I. (Cédula de Identidad): ")
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            correo = input("Correo electrónico: ")
            telefono = input("Teléfono: ")
            
            clientes.registrar_cliente(ci, nombre, apellido, correo, telefono)
            
        elif opcion == "2":
            print("\n-- Buscar Cliente --")
            ci = input("Ingrese la C.I. a buscar: ")
            datos = clientes.obtener_cliente(ci)
            
            if datos:
                print(f"\nDatos de C.I. {ci}:")
                print(f"Nombre completo: {datos['nombre']} {datos['apellido']}")
                print(f"Correo: {datos['correo']}")
                print(f"Teléfono: {datos['telefono']}")
                print(f"Pujas realizadas: {len(datos['historial_pujas'])}")
            else:
                print("Cliente no encontrado.")
                
        elif opcion == "3":
            print("\n-- Actualizar Correo --")
            ci = input("Ingrese la C.I. del cliente: ")
            if clientes.obtener_cliente(ci):
                nuevo_correo = input("Ingrese el nuevo correo: ")
                clientes.actualizar_correo(ci, nuevo_correo)
                print("Correo actualizado correctamente.")
            else:
                print("Cliente no encontrado.")
                
        elif opcion == "4":
            print("Saliendo del módulo de clientes...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

# Ejecutar el programa
if __name__ == "__main__":
    menu_principal()