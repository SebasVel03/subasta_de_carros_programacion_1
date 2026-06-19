import flet as ft
import datetime


# =====================================================================
# CLASES DE LOGIC DE NEGOCIO (POO)
# =====================================================================

class Cliente:
    def __init__(self, ci, nombre, apellido, correo, telefono):
        self.ci = ci
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.telefono = telefono
        self.historial_pujas = []

    def registrar_puja(self, puja):
        self.historial_pujas.append(puja)


class Puja:
    def __init__(self, cliente, monto):
        self.cliente = cliente          
        self.monto = monto              
        self.fecha_hora = datetime.datetime.now()


class Subasta:
    def __init__(self, id_subasta, carro, precio_base):
        self.id_subasta = id_subasta
        self.carro = carro              
        self.precio_base = precio_base
        self.activa = True
        self.lista_pujas = []           

    def recibir_puja(self, cliente, monto):
        if not self.activa:
            return False, "La subasta ya está cerrada."

        monto_actual_mas_alto = self.precio_base
        if self.lista_pujas:
            monto_actual_mas_alto = self.lista_pujas[-1].monto

        if monto <= monto_actual_mas_alto:
            return False, f"El monto debe superar la puja actual de ${monto_actual_mas_alto}."

        nueva_puja = Puja(cliente, monto)
        self.lista_pujas.append(nueva_puja)
        cliente.registrar_puja(nueva_puja)
        return True, f"¡Puja de ${monto} aceptada para el {self.carro}!"

    def obtener_ganador(self):
        if not self.lista_pujas:
            return None
        return self.lista_pujas[-1]


# =====================================================================
# APLICACIÓN INTERFAZ GRÁFICA CON FLET
# =====================================================================

class AppSubastas:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Sistema de Subastas de Carros"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 700
        self.page.window_height = 650
        
        # Simulación de Base de Datos en memoria
        self.registro_clientes = {}
        # Inicializamos una subasta activa por defecto para probar el módulo
        self.subasta_actual = Subasta(1, "Nissan Skyline R34 JDM", 35000)
        
        # Elementos visuales globales para actualizar dinámicamente
        self.txt_historial_pujas = ft.ListView(expand=1, spacing=10, padding=20)
        self.lbl_puja_mas_alta = ft.Text(f"Puja más alta actual: ${self.subasta_actual.precio_base}", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_ACCENT)
        self.dropdown_clientes = ft.Dropdown(label="Selecciona un Cliente para pujar", width=300)
        
        # Inicializar la interfaz
        self.construir_ui()

    def construir_ui(self):
        # --- PESTAÑA 1: REGISTRO DE CLIENTES ---
        self.input_ci = ft.TextField(label="Cédula de Identidad (C.I.)", width=300)
        self.input_nombre = ft.TextField(label="Nombre", width=300)
        self.input_apellido = ft.TextField(label="Apellido", width=300)
        self.input_correo = ft.TextField(label="Correo Electrónico", width=300)
        self.input_telefono = ft.TextField(label="Teléfono", width=300)
        self.lbl_status_registro = ft.Text("", size=14)

        vista_registro = ft.Column([
            ft.Text("Registrar Nuevo Cliente", size=24, weight=ft.FontWeight.BOLD),
            self.input_ci,
            self.input_nombre,
            self.input_apellido,
            self.input_correo,
            self.input_telefono,
            ft.ElevatedButton("Guardar Cliente", on_click=self.guardar_cliente_click, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE),
            self.lbl_status_registro
        ], scroll=ft.ScrollMode.AUTO, spacing=15)

        # --- PESTAÑA 2: MÓDULO DE SUBASTAS Y PUJAS ---
        self.input_monto_puja = ft.TextField(label="Monto a ofertar ($)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        self.lbl_status_puja = ft.Text("", size=14)

        vista_subasta = ft.Column([
            ft.Text(f"Subasta Activa: {self.subasta_actual.carro}", size=24, weight=ft.FontWeight.BOLD),
            self.lbl_puja_mas_alta,
            ft.Divider(),
            ft.Text("Realizar una Puja", size=18, weight=ft.FontWeight.SEMI_BOLD),
            self.dropdown_clientes,
            ft.Row([
                self.input_monto_puja,
                ft.ElevatedButton("Enviar Puja", on_click=self.enviar_puja_click, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE)
            ], spacing=10),
            self.lbl_status_puja,
            ft.Divider(),
            ft.Text("Historial de la Subasta en Vivo", size=16, weight=ft.FontWeight.SEMI_BOLD),
            self.txt_historial_pujas
        ], spacing=15, expand=True)

        # --- CONFIGURACIÓN DE LAS PESTAÑAS (TABS) ---
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Clientes", content=ft.Container(content=vista_registro, padding=20)),
                ft.Tab(text="Subasta & Pujas", content=ft.Container(content=vista_subasta, padding=20)),
            ],
            expand=1
        )
        
        self.page.add(tabs)

    def guardar_cliente_click(self, e):
        # Validar campos vacíos
        if not (self.input_ci.value and self.input_nombre.value and self.input_apellido.value):
            self.lbl_status_registro.value = "Por favor, llene los campos obligatorios (C.I., Nombre, Apellido)."
            self.lbl_status_registro.color = ft.colors.RED_400
            self.page.update()
            return

        ci = self.input_ci.value
        if ci in self.registro_clientes:
            self.lbl_status_registro.value = f"La C.I. {ci} ya está registrada."
            self.lbl_status_registro.color = ft.colors.RED_400
        else:
            # Creamos la instancia del cliente (POO)
            nuevo_cliente = Cliente(
                ci, self.input_nombre.value, self.input_apellido.value, 
                self.input_correo.value, self.input_telefono.value
            )
            self.registro_clientes[ci] = nuevo_cliente
            
            # Actualizamos el dropdown de la sección de subastas
            self.dropdown_clientes.options.append(
                ft.dropdown.Option(key=ci, text=f"{nuevo_cliente.nombre} {nuevo_cliente.apellido} (C.I. {ci})")
            )
            
            self.lbl_status_registro.value = f"¡{nuevo_cliente.nombre} registrado exitosamente!"
            self.lbl_status_registro.color = ft.colors.GREEN_400
            
            # Limpiar campos de texto
            self.input_ci.value = ""
            self.input_nombre.value = ""
            self.input_apellido.value = ""
            self.input_correo.value = ""
            self.input_telefono.value = ""
            
        self.page.update()

    def enviar_puja_click(self, e):
        if not self.dropdown_clientes.value:
            self.lbl_status_puja.value = "Seleccione un cliente de la lista."
            self.lbl_status_puja.color = ft.colors.RED_400
            self.page.update()
            return
        
        try:
            monto = float(self.input_monto_puja.value)
        except (ValueError, TypeError):
            self.lbl_status_puja.value = "Ingrese un número válido para el monto."
            self.lbl_status_puja.color = ft.colors.RED_400
            self.page.update()
            return

        # Obtenemos el objeto Cliente seleccionado desde nuestro diccionario
        cliente_que_puja = self.registro_clientes[self.dropdown_clientes.value]
        
        # Procesamos la puja usando el método de la clase Subasta (POO)
        exito, mensaje = self.subasta_actual.recibir_puja(cliente_que_puja, monto)
        
        if exito:
            self.lbl_status_puja.value = mensaje
            self.lbl_status_puja.color = ft.colors.GREEN_400
            self.lbl_puja_mas_alta.value = f"Puja más alta actual: ${monto} (Por: {cliente_que_puja.nombre})"
            
            # Insertar visualmente la puja en la lista gráfica
            hora_str = self.subasta_actual.lista_pujas[-1].fecha_hora.strftime('%H:%M:%S')
            self.txt_historial_pujas.controls.insert(
                0, ft.Text(f"[{hora_str}] {cliente_que_puja.nombre} ofertó ${monto}", color=ft.colors.BLUE_200)
            )
            self.input_monto_puja.value = ""
        else:
            self.lbl_status_puja.value = mensaje
            self.lbl_status_puja.color = ft.colors.RED_400
            
        self.page.update()

# --- EJECUCIÓN DE LA APLICACIÓN ---
if __name__ == "__main__":
    ft.app(target=AppSubastas)