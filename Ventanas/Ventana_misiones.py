import customtkinter as ctk
from tkinter import messagebox
import requests

class VentanaMisiones(ctk.CTkFrame):
    def __init__(self, padre, url_api):
        super().__init__(padre)
        self.url_api = url_api
        self.configurar_interfaz()
        self.cargar_misiones()
            
    def configurar_interfaz(self):
        # Título de la ventana
        etiqueta_titulo = ctk.CTkLabel(
            self,
            text="Gestión de Misiones",
            font=("Arial", 20, "bold")
        )
        etiqueta_titulo.pack(pady=(20, 10))
        
        # Panel izquierdo - Lista de misiones
        self.panel_izquierdo = ctk.CTkFrame(self, width=250)  # Establecer el ancho aquí
        self.panel_izquierdo.pack(side='left', fill='y', padx=10, pady=10, expand=False)
        
        # Panel derecho - Detalles y acciones
        self.panel_derecho = ctk.CTkFrame(self)
        self.panel_derecho.pack(side='right', fill='both', padx=10, pady=10, expand=True)
        
        # Configurar panel izquierdo
        self.configurar_panel_izquierdo()
        
        # Configurar panel derecho
        self.configurar_panel_derecho()
                
    def configurar_panel_izquierdo(self):
        # Título del panel
        titulo_lista = ctk.CTkLabel(
            self.panel_izquierdo,
            text="Misiones Disponibles",
            font=("Arial", 16, "bold")
        )
        titulo_lista.pack(pady=(0, 10))
        
        # Frame para la lista de misiones
        marco_lista = ctk.CTkFrame(self.panel_izquierdo)
        marco_lista.pack(fill='both', expand=True)
        
        # Lista de misiones (scrollable)
        self.marco_desplazable_misiones = ctk.CTkScrollableFrame(marco_lista)
        self.marco_desplazable_misiones.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Botón para crear nueva misión
        boton_nueva_mision = ctk.CTkButton(
            self.panel_izquierdo,
            text="Crear Nueva Misión",
            command=self.mostrar_crear_mision
        )
        boton_nueva_mision.pack(pady=10, padx=10, fill='x')
        
    def configurar_panel_derecho(self):
        # Inicialmente, el panel derecho muestra un mensaje
        self.mensaje_inicial = ctk.CTkLabel(
            self.panel_derecho,
            text="Selecciona una misión para ver sus detalles\no crea una nueva",
            font=("Arial", 14),
            justify='center'
        )
        self.mensaje_inicial.pack(pady=50)
        
        # Panel de creación de misión (oculto inicialmente)
        self.panel_creacion = ctk.CTkFrame(self.panel_derecho)
        
        titulo_creacion = ctk.CTkLabel(
            self.panel_creacion,
            text="Crear Nueva Misión",
            font=("Arial", 16, "bold")
        )
        titulo_creacion.pack(pady=(20, 10))
        
        # Form para crear misión
        marco_formulario = ctk.CTkFrame(self.panel_creacion)
        marco_formulario.pack(fill='x', padx=20, pady=10)
        
        # Título de la misión
        marco_titulo = ctk.CTkFrame(marco_formulario)
        marco_titulo.pack(fill='x', pady=(0, 10))
        
        etiqueta_titulo = ctk.CTkLabel(
            marco_titulo,
            text="Título:",
            width=100
        )
        etiqueta_titulo.pack(side='left', padx=(0, 10))
        
        self.entrada_titulo_mision = ctk.CTkEntry(
            marco_titulo,
            width=300
        )
        self.entrada_titulo_mision.pack(side='left', fill='x', expand=True)
        
        # Descripción
        marco_descripcion = ctk.CTkFrame(marco_formulario)
        marco_descripcion.pack(fill='x', pady=(0, 10))
        
        etiqueta_descripcion = ctk.CTkLabel(
            marco_descripcion,
            text="Descripción:",
            width=100
        )
        etiqueta_descripcion.pack(side='left', padx=(0, 10), anchor='n', pady=5)
        
        self.texto_descripcion_mision = ctk.CTkTextbox(
            marco_descripcion,
            width=300,
            height=150
        )
        self.texto_descripcion_mision.pack(side='left', fill='both', expand=True)
        
        # Recompensa XP
        marco_experiencia = ctk.CTkFrame(marco_formulario)
        marco_experiencia.pack(fill='x', pady=(0, 10))
        
        etiqueta_experiencia = ctk.CTkLabel(
            marco_experiencia,
            text="XP Reward:",
            width=100
        )
        etiqueta_experiencia.pack(side='left', padx=(0, 10))
        
        self.entrada_experiencia_mision = ctk.CTkEntry(
            marco_experiencia,
            width=100
        )
        self.entrada_experiencia_mision.pack(side='left')
        self.entrada_experiencia_mision.insert(0, "10")
        
        # Botón de guardar
        boton_guardar = ctk.CTkButton(
            self.panel_creacion,
            text="Guardar Misión",
            command=self.crear_mision
        )
        boton_guardar.pack(pady=20)
        
        # Panel de detalles de la misión (oculto inicialmente)
        self.panel_detalles = ctk.CTkFrame(self.panel_derecho)
        
        self.titulo_detalles = ctk.CTkLabel(
            self.panel_detalles,
            text="Detalles de la Misión",
            font=("Arial", 16, "bold")
        )
        self.titulo_detalles.pack(pady=(20, 10))
        
        # Info de la misión
        self.marco_informacion = ctk.CTkFrame(self.panel_detalles)
        self.marco_informacion.pack(fill='x', padx=20, pady=10, expand=True)
        
    def cargar_misiones(self):
        """Carga las misiones desde la API"""
        try:
            respuesta = requests.get(f"{self.url_api}/misiones")
            if respuesta.status_code == 200:
                misiones = respuesta.json()
                
                # Limpiar el frame actual
                for widget in self.marco_desplazable_misiones.winfo_children():
                    widget.destroy()
                
                # Crear un botón para cada misión
                if not misiones:
                    etiqueta_vacia = ctk.CTkLabel(
                        self.marco_desplazable_misiones,
                        text="No hay misiones disponibles",
                        font=("Arial", 12)
                    )
                    etiqueta_vacia.pack(pady=20)
                else:
                    for mision in misiones:
                        boton = ctk.CTkButton(
                            self.marco_desplazable_misiones,
                            text=f"{mision['titulo']}",
                            command=lambda m=mision: self.mostrar_detalles_mision(m)
                        )
                        boton.pack(fill='x', pady=2)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar misiones: {str(e)}")
    
    def mostrar_crear_mision(self):
        """Muestra el panel de creación de misiones"""
        self.mensaje_inicial.pack_forget()
        self.panel_detalles.pack_forget()
        self.panel_creacion.pack(fill='both', expand=True)
        
    def crear_mision(self):
        """Crea una nueva misión"""
        titulo = self.entrada_titulo_mision.get().strip()
        descripcion = self.texto_descripcion_mision.get("1.0", "end-1c").strip()
        
        try:
            recompensa_experiencia = float(self.entrada_experiencia_mision.get().strip())
        except ValueError:
            messagebox.showwarning("Advertencia", "La recompensa XP debe ser un número válido")
            return
            
        if not titulo:
            messagebox.showwarning("Advertencia", "Debe ingresar un título para la misión")
            return
            
        try:
            respuesta = requests.post(
                f"{self.url_api}/misiones",
                json={
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "recompensa_experiencia": recompensa_experiencia
                }
            )
            
            if respuesta.status_code == 200:
                messagebox.showinfo("Éxito", f"Misión '{titulo}' creada correctamente")
                self.entrada_titulo_mision.delete(0, 'end')
                self.texto_descripcion_mision.delete("1.0", "end")
                self.entrada_experiencia_mision.delete(0, 'end')
                self.entrada_experiencia_mision.insert(0, "10")
                
                self.cargar_misiones()
                self.panel_creacion.pack_forget()
                self.mensaje_inicial.pack(pady=50)
            else:
                messagebox.showerror("Error", f"Error al crear misión: {respuesta.text}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear misión: {str(e)}")
    
    def mostrar_detalles_mision(self, mision):
        """Muestra los detalles de una misión"""
        # Ocultar otros paneles
        self.mensaje_inicial.pack_forget()
        self.panel_creacion.pack_forget()
        
        # Mostrar panel de detalles
        self.panel_detalles.pack(fill='both', expand=True)
        
        # Actualizar título
        self.titulo_detalles.configure(text=f"Detalles de la Misión")
        
        # Limpiar y actualizar información
        for widget in self.marco_informacion.winfo_children():
            widget.destroy()
        
        # Crear etiquetas de información
        etiqueta_titulo = ctk.CTkLabel(
            self.marco_informacion,
            text=mision['titulo'],
            font=("Arial", 18, "bold")
        )
        etiqueta_titulo.pack(fill='x', padx=10, pady=(10, 5), anchor='w')
        
        # Línea separadora
        separador = ctk.CTkFrame(self.marco_informacion, height=2)
        separador.pack(fill='x', padx=10, pady=5)
        
        # Descripción
        titulo_descripcion = ctk.CTkLabel(
            self.marco_informacion,
            text="Descripción:",
            font=("Arial", 14, "bold"),
            anchor='w'
        )
        titulo_descripcion.pack(fill='x', padx=10, pady=(10, 5), anchor='w')
        
        texto_descripcion = mision.get('descripcion', 'Sin descripción')
        etiqueta_descripcion = ctk.CTkLabel(
            self.marco_informacion,
            text=texto_descripcion,
            font=("Arial", 12),
            anchor='w',
            justify='left',
            wraplength=400
        )
        etiqueta_descripcion.pack(fill='x', padx=10, pady=(0, 10), anchor='w')
        
        # Recompensa
        titulo_recompensa = ctk.CTkLabel(
            self.marco_informacion,
            text="Recompensa:",
            font=("Arial", 14, "bold"),
            anchor='w'
        )
        titulo_recompensa.pack(fill='x', padx=10, pady=(10, 5), anchor='w')
        
        texto_recompensa = f"{mision['recompensa_experiencia']} XP"
        etiqueta_recompensa = ctk.CTkLabel(
            self.marco_informacion,
            text=texto_recompensa,
            font=("Arial", 12),
            anchor='w'
        )
        etiqueta_recompensa.pack(fill='x', padx=10, pady=(0, 10), anchor='w')
        
        # Botón para asignar a personaje
        boton_asignar = ctk.CTkButton(
            self.marco_informacion,
            text="Asignar a Personaje",
            command=lambda m=mision: self.mostrar_personajes_para_mision(m)
        )
        boton_asignar.pack(pady=20)
    
    def mostrar_personajes_para_mision(self, mision):
        """Muestra ventana para seleccionar un personaje"""
        # Crear ventana emergente
        self.ventana_asignacion = ctk.CTkToplevel(self)
        self.ventana_asignacion.title("Seleccionar Personaje")
        self.ventana_asignacion.geometry("400x500")
        self.ventana_asignacion.transient(self)
        self.ventana_asignacion.grab_set()
        
        # Título
        etiqueta_titulo = ctk.CTkLabel(
            self.ventana_asignacion,
            text=f"Asignar: {mision['titulo']}",
            font=("Arial", 16, "bold")
        )
        etiqueta_titulo.pack(pady=(20, 10))
        
        # Frame para lista de personajes
        marco_lista_personajes = ctk.CTkFrame(self.ventana_asignacion)
        marco_lista_personajes.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Cargar personajes disponibles
        try:
            respuesta = requests.get(f"{self.url_api}/personajes")
            
            if respuesta.status_code == 200:
                personajes = respuesta.json()
                
                if not personajes:
                    etiqueta_vacia = ctk.CTkLabel(
                        marco_lista_personajes,
                        text="No hay personajes disponibles",
                        font=("Arial", 12)
                    )
                    etiqueta_vacia.pack(pady=20)
                else:
                    # Scrollable frame
                    marco_desplazable = ctk.CTkScrollableFrame(marco_lista_personajes)
                    marco_desplazable.pack(fill='both', expand=True, padx=5, pady=5)
                    
                    # Crear un botón para cada personaje
                    for personaje in personajes:
                        boton = ctk.CTkButton(
                            marco_desplazable,
                            text=f"{personaje['nombre']} (Nivel {personaje['nivel']})",
                            command=lambda p=personaje, m=mision: self.asignar_a_personaje(p['id'], m['id'])
                        )
                        boton.pack(fill='x', pady=2)
            else:
                messagebox.showerror("Error", "No se pudieron obtener los personajes.")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al conectar con la API:\n{e}")