from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import json
from typing import List, Dict, Any, Optional

Base = declarative_base()

# Tabla de asociación para la relación muchos a muchos entre personajes y misiones
personaje_mision = Table(
    "personaje_mision",
    Base.metadata,
    Column("personaje_id", Integer, ForeignKey("personajes.id")),
    Column("mision_id", Integer, ForeignKey("misiones.id")),
    Column("orden", Integer),  # Para mantener el orden FIFO
)

class Personaje(Base):
    """Modelo de personaje para el juego RPG"""
    __tablename__ = "personajes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    nivel = Column(Integer, default=1)
    experiencia = Column(Float, default=0)
    
    # Relación muchos a muchos con misiones
    misiones = relationship(
        "Mision",
        secondary=personaje_mision,
        back_populates="personajes",
        order_by=lambda: personaje_mision.c.orden
    )
    
    def agregar_experiencia(self, cantidad: float) -> None:
        """Añade experiencia al personaje y sube de nivel si corresponde"""
        self.experiencia += cantidad
        # Algoritmo simple de nivel: cada 100 XP se sube de nivel
        nuevo_nivel = int(self.experiencia / 100) + 1
        if nuevo_nivel > self.nivel:
            self.nivel = nuevo_nivel
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte el personaje a un diccionario para serialización"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "nivel": self.nivel,
            "experiencia": self.experiencia,
            "cantidad_misiones": len(self.misiones)
        }

class Mision(Base):
    """Modelo de misión para el juego RPG"""
    __tablename__ = "misiones"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descripcion = Column(String)
    recompensa_experiencia = Column(Float)
    
    # Relación muchos a muchos con personajes
    personajes = relationship(
        "Personaje",
        secondary=personaje_mision,
        back_populates="misiones"
    )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la misión a un diccionario para serialización"""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "recompensa_experiencia": self.recompensa_experiencia
        }

# Configuración de la base de datos
URL_BASE_DATOS = "sqlite:///./rpg_game.db"
engine = create_engine(URL_BASE_DATOS)
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def obtener_db():
    """Función para obtener una sesión de base de datos"""
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()

def crear_tablas():
    """Crea todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)