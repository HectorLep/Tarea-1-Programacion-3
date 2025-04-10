import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
from Ventanas import util_ventana
from Ventanas.Ventana_personajes import VentanaPersonajes
from Ventanas.Ventana_misiones import VentanaMisiones

class Main(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RPG Mission System")
        self.geometry("850x700")
        self.config_window()
        self.api_url = "http://localhost:8000"  # URL de FastAPI
        
        # Configuración de frames principales
        self.setup_frames()
        
        # Configuración de elementos de la interfaz
        self.controles_barra_superior()
        self.controles_barra_lateral()
        
        # Ventana actual
        self.current_frame = None
        
        # Iniciar en la pantalla de inicio
        self.mostrar_inicio()

    def config_window(self):
        util_ventana.centrar_ventana(self, 850, 700)
        
    def setup_frames(self):
        # Barra superior
        self.barra_superior = ctk.CTkFrame(self, height=70, corner_radius=0)
        self.barra_superior.pack(fill='x', side='top')
        
        # Panel lateral
        self.menu_lateral = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.menu_lateral.pack(fill='y', side='left', padx=0, pady=0)
        
        # Panel principal donde se mostrarán las diferentes ventanas
        self.panel_principal = ctk.CTkFrame(self)
        self.panel_principal.pack(fill='both', expand=True, padx=10, pady=10)

    def controles_barra_superior(self):
        self.labelTitulo = ctk.CTkLabel(
            self.barra_superior, 
            text='Sistema de Misiones RPG', 
            font=('Arial', 24, 'bold')
        )
        self.labelTitulo.pack(side='left', padx=20, pady=10)

    def controles_barra_lateral(self):
        # Título del menú
        menu_title = ctk.CTkLabel(
            self.menu_lateral,
            text="MENÚ",
            font=("Arial", 16, "bold")
        )
        menu_title.pack(pady=(20, 10))
        
        # Botones del menú
        self.btn_inicio = ctk.CTkButton(
            self.menu_lateral,
            text="Inicio",
            command=self.mostrar_inicio,
            width=180
        )
        self.btn_inicio.pack(pady=5, padx=10)
        
        self.btn_personajes = ctk.CTkButton(
            self.menu_lateral,
            text="Personajes",
            command=self.mostrar_personajes,
            width=180
        )
        self.btn_personajes.pack(pady=5, padx=10)
        
        self.btn_misiones = ctk.CTkButton(
            self.menu_lateral,
            text="Misiones",
            command=self.mostrar_misiones,
            width=180
        )
        self.btn_misiones.pack(pady=5, padx=10)
        
        # Información
        info_frame = ctk.CTkFrame(self.menu_lateral)
        info_frame.pack(side='bottom', fill='x', padx=10, pady=20)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="Sistema de Misiones RPG\nImplementación de TDA Cola",
            font=("Arial", 10),
            justify='center'
        )
        info_label.pack(pady=10)

    def cambiar_frame(self, new_frame):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = new_frame
        self.current_frame.pack(fill='both', expand=True)

    def mostrar_inicio(self):
        # Crear frame de inicio
        frame_inicio = ctk.CTkFrame(self.panel_principal)
        
        # Título de bienvenida
        welcome_label = ctk.CTkLabel(
            frame_inicio,
            text="Bienvenido al Sistema de Misiones RPG",
            font=("Arial", 24, "bold")
        )
        welcome_label.pack(pady=(50, 20))
        
        # Descripción
        desc_text = (
            "Este sistema permite gestionar personajes y misiones en un juego RPG.\n\n"
            "Características principales:\n"
            "• Implementación de TDA Cola (FIFO) para gestionar misiones\n"
            "• Integración con base de datos SQLAlchemy\n"
            "• API REST completa con FastAPI\n\n"
            "Selecciona una opción del menú para comenzar."
        )
        
        desc_label = ctk.CTkLabel(
            frame_inicio,
            text=desc_text,
            font=("Arial", 14),
            justify='center'
        )
        desc_label.pack(pady=20)
        
        # Botones de acción rápida
        quick_buttons_frame = ctk.CTkFrame(frame_inicio)
        quick_buttons_frame.pack(pady=30)
        
        btn_crear_personaje = ctk.CTkButton(
            quick_buttons_frame,
            text="Crear Personaje",
            command=self.mostrar_personajes,
            width=150,
            height=40
        )
        btn_crear_personaje.pack(side='left', padx=10)
        
        btn_ver_misiones = ctk.CTkButton(
            quick_buttons_frame,
            text="Ver Misiones",
            command=self.mostrar_misiones,
            width=150,
            height=40
        )
        btn_ver_misiones.pack(side='left', padx=10)
        
        self.cambiar_frame(frame_inicio)

    def mostrar_personajes(self):
        frame_personajes = VentanaPersonajes(self.panel_principal, self.api_url)
        self.cambiar_frame(frame_personajes)

    def mostrar_misiones(self):
        frame_misiones = VentanaMisiones(self.panel_principal, self.api_url)
        self.cambiar_frame(frame_misiones)