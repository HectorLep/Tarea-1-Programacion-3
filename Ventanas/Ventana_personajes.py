import customtkinter as ctk
from tkinter import messagebox
import requests

class VentanaPersonajes(ctk.CTkFrame):
    def __init__(self, padre, url_api):
        super().__init__(padre)
        self.url_api = url_api
        self.configurar_interfaz()
        self.cargar_personajes()
        
    def configurar_interfaz(self):
        # Título de la ventana
        etiqueta_titulo = ctk.CTkLabel(
            self,
            text="Gestión de Personajes",
            font=("Arial", 20, "bold")
        )
        etiqueta_titulo.pack(pady=(20, 10))
        
        # Panel izquierdo - Lista de personajes
        self.panel_izquierdo = ctk.CTkFrame(self)
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
            text="Personajes",
            font=("Arial", 16, "bold")
        )
        titulo_lista.pack(pady=(0, 10))
        
        # Frame para la lista de personajes
        marco_lista = ctk.CTkFrame(self.panel_izquierdo)
        marco_lista.pack(fill='both', expand=True)
        
        # Lista de personajes (simulada con botones)
        self.marco_personajes = ctk.CTkFrame(marco_lista)
        self.marco_personajes.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Botón para crear nuevo personaje
        boton_nuevo_personaje = ctk.CTkButton(
            self.panel_izquierdo,
            text="Crear Nuevo Personaje",
            command=self.mostrar_crear_personaje
        )
        boton_nuevo_personaje.pack(pady=10, padx=10, fill='x')
        
    def configurar_panel_derecho(self):
        # Inicialmente, el panel derecho muestra un mensaje
        self.mensaje_inicial = ctk.CTkLabel(
            self.panel_derecho,
            text="Selecciona un personaje para ver sus detalles",
            font=("Arial", 14)
        )
        self.mensaje_inicial.pack(pady=50)
        
        # Panel de creación de personaje (oculto inicialmente)
        self.panel_creacion = ctk.CTkFrame(self.panel_derecho)
        
        titulo_creacion = ctk.CTkLabel(
            self.panel_creacion,
            text="Crear Nuevo Personaje",
            font=("Arial", 16, "bold")
        )
        titulo_creacion.pack(pady=(20, 10))
        
        # Nombre del personaje
        marco_nombre = ctk.CTkFrame(self.panel_creacion)
        marco_nombre.pack(fill='x', padx=20, pady=10)
        
        etiqueta_nombre = ctk.CTkLabel(
            marco_nombre,
            text="Nombre:",
            width=100
        )
        etiqueta_nombre.pack(side='left', padx=(0, 10))
        
        self.entrada_nombre_personaje = ctk.CTkEntry(
            marco_nombre,
            width=200
        )
        self.entrada_nombre_personaje.pack(side='left', fill='x', expand=True)
        
        # Botón de guardar
        boton_guardar = ctk.CTkButton(
            self.panel_creacion,
            text="Guardar Personaje",
            command=self.crear_personaje
        )
        boton_guardar.pack(pady=20)
        
        # Panel de detalles del personaje (oculto inicialmente)
        self.panel_detalles = ctk.CTkFrame(self.panel_derecho)
        
        self.titulo_detalles = ctk.CTkLabel(
            self.panel_detalles,
            text="Detalles del Personaje",
            font=("Arial", 16, "bold")
        )
        self.titulo_detalles.pack(pady=(20, 10))
        
        # Info del personaje
        self.marco_informacion = ctk.CTkFrame(self.panel_detalles)
        self.marco_informacion.pack(fill='x', padx=20, pady=10)
        
        # Caja para misiones pendientes
        titulo_misiones = ctk.CTkLabel(
            self.panel_detalles,
            text="Cola de Misiones (FIFO)",
            font=("Arial", 14, "bold")
        )
        titulo_misiones.pack(pady=(20, 10))
        
        self.marco_misiones = ctk.CTkFrame(self.panel_detalles)
        self.marco_misiones.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Botones de acción
        marco_acciones = ctk.CTkFrame(self.panel_detalles)
        marco_acciones.pack(fill='x', padx=20, pady=20)
        
        self.boton_completar = ctk.CTkButton(
            marco_acciones,
            text="Completar Primera Misión",
            command=self.completar_mision
        )
        self.boton_completar.pack(side='left', padx=5)
        
        self.boton_asignar = ctk.CTkButton(
            marco_acciones,
            text="Asignar Nueva Misión",
            command=self.mostrar_asignar_mision
        )
        self.boton_asignar.pack(side='left', padx=5)
        
         
        
    def cargar_personajes(self):
        """Carga los personajes desde la API"""
        try:
            respuesta = requests.get(f"{self.url_api}/personajes")
            if respuesta.status_code == 200:
                personajes = respuesta.json()
                
                # Limpiar el frame actual
                for widget in self.marco_personajes.winfo_children():
                    widget.destroy()
                
                # Crear un botón para cada personaje
                for personaje in personajes:
                    boton = ctk.CTkButton(
                        self.marco_personajes,
                        text=f"{personaje['nombre']} (Nivel {personaje['nivel']})",
                        command=lambda p=personaje: self.mostrar_detalles_personaje(p['id'])
                    )
                    boton.pack(fill='x', pady=2)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar personajes: {str(e)}")
    
    def mostrar_crear_personaje(self):
        """Muestra el panel de creación de personajes"""
        self.mensaje_inicial.pack_forget()
        self.panel_detalles.pack_forget()
        self.panel_creacion.pack(fill='both', expand=True)
        
    def crear_personaje(self):
        """Crea un nuevo personaje"""
        nombre = self.entrada_nombre_personaje.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre para el personaje")
            return
            
        try:
            respuesta = requests.post(
                f"{self.url_api}/personajes",
                json={"nombre": nombre}
            )
            
            if respuesta.status_code == 200:
                messagebox.showinfo("Éxito", f"Personaje '{nombre}' creado correctamente")
                self.entrada_nombre_personaje.delete(0, 'end')
                self.cargar_personajes()
                self.panel_creacion.pack_forget()
                self.mensaje_inicial.pack(pady=50)
            else:
                messagebox.showerror("Error", f"Error al crear personaje: {respuesta.text}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear personaje: {str(e)}")
    
    def mostrar_detalles_personaje(self, id_personaje):
        """Muestra los detalles de un personaje"""
        try:
            # Obtener información del personaje
            respuesta = requests.get(f"{self.url_api}/personajes/{id_personaje}/misiones")
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                personaje = datos["personaje"]
                misiones = datos["misiones"]
                
                # Ocultar otros paneles
                self.mensaje_inicial.pack_forget()
                self.panel_creacion.pack_forget()
                
                # Mostrar panel de detalles
                self.panel_detalles.pack(fill='both', expand=True)
                
                # Actualizar título
                self.titulo_detalles.configure(text=f"Detalles de {personaje['nombre']}")
                
                # Limpiar y actualizar información
                for widget in self.marco_informacion.winfo_children():
                    widget.destroy()
                
                # Crear etiquetas de información
                texto_informacion = f"""
                Nombre: {personaje['nombre']}
                Nivel: {personaje['nivel']}
                Experiencia: {personaje['experiencia']} XP
                Misiones pendientes: {personaje['cantidad_misiones']}
                """
                
                etiqueta_informacion = ctk.CTkLabel(
                    self.marco_informacion,
                    text=texto_informacion,
                    justify='left',
                    font=("Arial", 12)
                )
                etiqueta_informacion.pack(fill='x', padx=10, pady=10)
                
                # Guardar el ID del personaje actual
                self.id_personaje_actual = id_personaje
                
                # Mostrar cola de misiones
                self.actualizar_lista_misiones(misiones)
                
            else:
                messagebox.showerror("Error", f"Error al cargar detalles: {respuesta.text}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
    
    def actualizar_lista_misiones(self, misiones):
        """Actualiza la lista de misiones"""
        # Limpiar la lista actual
        for widget in self.marco_misiones.winfo_children():
            widget.destroy()
            
        if not misiones:
            etiqueta_vacia = ctk.CTkLabel(
                self.marco_misiones,
                text="No hay misiones pendientes",
                font=("Arial", 12)
            )
            etiqueta_vacia.pack(pady=20)
            self.boton_completar.configure(state="disabled")
        else:
            self.boton_completar.configure(state="normal")
            
            # Crear un frame para cada misión
            for i, mision in enumerate(misiones):
                marco_mision = ctk.CTkFrame(self.marco_misiones)
                marco_mision.pack(fill='x', pady=5, padx=5)
                
                # Indicador de posición
                indicador_posicion = ctk.CTkLabel(
                    marco_mision,
                    text=f"{i+1}",
                    width=30,
                    fg_color=("#3a7ebf" if i == 0 else "transparent"),
                    text_color=("white" if i == 0 else "black"),
                    corner_radius=15
                )
                indicador_posicion.pack(side='left', padx=5)
                
                # Detalles de la misión
                detalles_mision = ctk.CTkLabel(
                    marco_mision,
                    text=f"{mision['titulo']} - XP: {mision['recompensa_experiencia']}",
                    anchor='w'
                )
                detalles_mision.pack(side='left', fill='x', expand=True, padx=5)
    
    def completar_mision(self):
        """Completa la primera misión en la cola"""
        if not hasattr(self, 'id_personaje_actual'):
            return
            
        try:
            respuesta = requests.post(f"{self.url_api}/personajes/{self.id_personaje_actual}/completar")
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                messagebox.showinfo("Misión Completada", datos["mensaje"])
                
                # Actualizar detalles del personaje
                self.mostrar_detalles_personaje(self.id_personaje_actual)
            else:
                messagebox.showerror("Error", f"Error al completar misión: {respuesta.text}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al completar misión: {str(e)}")
        
    def mostrar_asignar_mision(self):
        """Muestra ventana para asignar una nueva misión"""
        if not hasattr(self, 'id_personaje_actual'):
            return
        
        # Crear ventana emergente
        self.ventana_asignacion = ctk.CTkToplevel(self)
        self.ventana_asignacion.title("Asignar Nueva Misión")
        self.ventana_asignacion.geometry("400x500")
        self.ventana_asignacion.transient(self)
        
        # Asegurarse de que la ventana sea visible antes de usar grab_set
        self.ventana_asignacion.wait_visibility()
        self.ventana_asignacion.after(100, self.ventana_asignacion.grab_set)
        
        # Título
        etiqueta_titulo = ctk.CTkLabel(
            self.ventana_asignacion,
            text="Seleccionar Misión",
            font=("Arial", 16, "bold")
        )
        etiqueta_titulo.pack(pady=(20, 10))
        
        # Frame para lista de misiones
        marco_lista_misiones = ctk.CTkFrame(self.ventana_asignacion)
        marco_lista_misiones.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Cargar misiones disponibles
        try:
            respuesta = requests.get(f"{self.url_api}/misiones")
            
            if respuesta.status_code == 200:
                misiones = respuesta.json()
                
                if not misiones:
                    etiqueta_vacia = ctk.CTkLabel(
                        marco_lista_misiones,
                        text="No hay misiones disponibles",
                        font=("Arial", 12)
                    )
                    etiqueta_vacia.pack(pady=20)
                else:
                    # Scrollable frame
                    marco_desplazable = ctk.CTkScrollableFrame(marco_lista_misiones)
                    marco_desplazable.pack(fill='both', expand=True, padx=5, pady=5)
                    
                    # Crear un botón para cada misión
                    for mision in misiones:
                        boton = ctk.CTkButton(
                            marco_desplazable,
                            text=f"{mision['titulo']} - XP: {mision['recompensa_experiencia']}",
                            command=lambda m=mision: self.asignar_mision(m['id'])
                        )
                        boton.pack(fill='x', pady=2)
            else:
                messagebox.showerror("Error", f"Error al cargar misiones: {respuesta.text}")
                self.ventana_asignacion.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar misiones: {str(e)}")
            self.ventana_asignacion.destroy()
                
    def asignar_mision(self, id_mision):
        """Asigna una misión al personaje actual"""
        if not hasattr(self, 'id_personaje_actual'):
            self.ventana_asignacion.destroy()
            return
            
        try:
            respuesta = requests.post(
                f"{self.url_api}/personajes/{self.id_personaje_actual}/misiones/{id_mision}"
            )
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                messagebox.showinfo("Misión Asignada", datos["mensaje"])
                
                # Cerrar ventana emergente
                self.ventana_asignacion.destroy()
                
                # Actualizar detalles del personaje
                self.mostrar_detalles_personaje(self.id_personaje_actual)
            else:
                messagebox.showerror("Error", f"Error al asignar misión: {respuesta.text}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al asignar misión: {str(e)}")
            self.ventana_asignacion.destroy()