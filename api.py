from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from pydantic import BaseModel

from models import obtener_db, Personaje, Mision, crear_tablas
from tda_cola import Cola

app = FastAPI(title="Sistema de Misiones RPG")

# Creación de tablas
crear_tablas()

# Modelos Pydantic para validación de datos
class CrearPersonaje(BaseModel):
    nombre: str

class CrearMision(BaseModel):
    titulo: str
    descripcion: str
    recompensa_experiencia: float

class RespuestaPersonaje(BaseModel):
    id: int
    nombre: str
    nivel: int
    experiencia: float
    cantidad_misiones: int

class RespuestaMision(BaseModel):
    id: int
    titulo: str
    descripcion: str
    recompensa_experiencia: float

# Endpoints
@app.post("/personajes", response_model=RespuestaPersonaje)
def crear_personaje(personaje: CrearPersonaje, db: Session = Depends(obtener_db)):
    """Crea un nuevo personaje"""
    db_personaje = Personaje(nombre=personaje.nombre)
    db.add(db_personaje)
    db.commit()
    db.refresh(db_personaje)
    return db_personaje.a_diccionario()

@app.post("/misiones", response_model=RespuestaMision)
def crear_mision(mision: CrearMision, db: Session = Depends(obtener_db)):
    """Crea una nueva misión"""
    db_mision = Mision(
        titulo=mision.titulo,
        descripcion=mision.descripcion,
        recompensa_experiencia=mision.recompensa_experiencia
    )
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)
    return db_mision.a_diccionario()

@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(obtener_db)):
    """Acepta una misión para un personaje (encola)"""
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    mision = db.query(Mision).filter(Mision.id == mision_id).first()
    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")
    
    # Verificar si la misión ya está asignada
    for mision_existente in personaje.misiones:
        if mision_existente.id == mision_id:
            raise HTTPException(status_code=400, detail="Misión ya asignada al personaje")
    
    # Encontrar el último orden para este personaje
    siguiente_orden = 1
    from sqlalchemy import select, func
    from models import personaje_mision
    
    consulta = select(func.max(personaje_mision.c.orden)).where(
        personaje_mision.c.personaje_id == personaje_id
    )
    resultado = db.execute(consulta).scalar()
    if resultado:
        siguiente_orden = resultado + 1
    
    # Añadir la misión al final de la cola (FIFO)
    consulta = personaje_mision.insert().values(
        personaje_id=personaje_id,
        mision_id=mision_id,
        orden=siguiente_orden
    )
    db.execute(consulta)
    db.commit()
    
    return {"estado": "éxito", "mensaje": f"Misión {mision.titulo} añadida a la cola del personaje {personaje.nombre}"}

@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(obtener_db)):
    """Completa la primera misión en la cola (desencola) y suma XP"""
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    # Si no hay misiones en cola
    if not personaje.misiones:
        raise HTTPException(status_code=400, detail="No hay misiones pendientes")
    
    # Obtener la primera misión (FIFO)
    primera_mision = personaje.misiones[0]
    
    # Sumar XP
    personaje.agregar_experiencia(primera_mision.recompensa_experiencia)
    
    # Eliminar la misión de la cola
    from sqlalchemy import delete
    from models import personaje_mision
    
    consulta = delete(personaje_mision).where(
        personaje_mision.c.personaje_id == personaje_id,
        personaje_mision.c.mision_id == primera_mision.id
    )
    db.execute(consulta)
    
    # Reordenar las misiones restantes
    for i, mision in enumerate(personaje.misiones[1:], 1):
        consulta = personaje_mision.update().where(
            personaje_mision.c.personaje_id == personaje_id,
            personaje_mision.c.mision_id == mision.id
        ).values(orden=i)
        db.execute(consulta)
    
    db.commit()
    
    return {
        "estado": "éxito", 
        "mensaje": f"Misión {primera_mision.titulo} completada. +{primera_mision.recompensa_experiencia} XP",
        "personaje": personaje.a_diccionario()
    }

@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones_personaje(personaje_id: int, db: Session = Depends(obtener_db)):
    """Lista las misiones de un personaje en orden FIFO"""
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    return {
        "personaje": personaje.a_diccionario(),
        "misiones": [mision.a_diccionario() for mision in personaje.misiones]
    }

@app.get("/personajes")
def listar_personajes(db: Session = Depends(obtener_db)):
    """Lista todos los personajes"""
    personajes = db.query(Personaje).all()
    return [personaje.a_diccionario() for personaje in personajes]

@app.get("/misiones")
def listar_misiones(db: Session = Depends(obtener_db)):
    """Lista todas las misiones disponibles"""
    misiones = db.query(Mision).all()
    return [mision.a_diccionario() for mision in misiones]