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

# Diccionario para almacenar colas temporales por personaje (en memoria)
colas_personajes: Dict[int, Cola[Mision]] = {}

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
    """Crea un nuevo personaje y le asigna una cola vacía"""
    db_personaje = Personaje(nombre=personaje.nombre)
    db.add(db_personaje)
    db.commit()
    db.refresh(db_personaje)
    
    # Crear una cola vacía para este personaje en memoria
    colas_personajes[db_personaje.id] = Cola()
    
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
    """Acepta una misión y la añade a la cola temporal del personaje"""
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    mision = db.query(Mision).filter(Mision.id == mision_id).first()
    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")
    
    # Verificar si la misión ya está en la cola del personaje
    if personaje_id in colas_personajes:
        cola = colas_personajes[personaje_id]
        for m in cola:  # Iteramos sobre la cola usando __iter__
            if m.id == mision_id:
                raise HTTPException(status_code=400, detail="Misión ya asignada al personaje")
    else:
        colas_personajes[personaje_id] = Cola()  # Si no existe, creamos la cola
    
    # Añadir la misión a la cola temporal usando el TDA Cola
    colas_personajes[personaje_id].agregar(mision)
    
    # Guardar en la base de datos también (sincronización)
    from sqlalchemy import select, func
    from models import personaje_mision
    
    siguiente_orden = 1
    consulta = select(func.max(personaje_mision.c.orden)).where(
        personaje_mision.c.personaje_id == personaje_id
    )
    resultado = db.execute(consulta).scalar()
    if resultado:
        siguiente_orden = resultado + 1
    
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
    """Completa la primera misión en la cola temporal y actualiza la base de datos"""
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    # Verificar si hay misiones en la cola temporal
    if personaje_id not in colas_personajes or colas_personajes[personaje_id].esta_vacia():
        raise HTTPException(status_code=400, detail="No hay misiones pendientes")
    
    # Sacar la primera misión de la cola temporal usando el TDA Cola
    primera_mision = colas_personajes[personaje_id].sacar()
    
    # Sumar experiencia al personaje
    personaje.agregar_experiencia(primera_mision.recompensa_experiencia)
    
    # Eliminar la misión de la base de datos
    from sqlalchemy import delete
    from models import personaje_mision
    
    consulta = delete(personaje_mision).where(
        personaje_mision.c.personaje_id == personaje_id,
        personaje_mision.c.mision_id == primera_mision.id
    )
    db.execute(consulta)
    
    # Reordenar las misiones restantes en la base de datos
    for i, mision in enumerate(personaje.misiones, 1):  # Usamos las misiones restantes de la DB
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
    """Lista las misiones de un personaje desde la cola temporal y la base de datos"""
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    # Obtener las misiones de la cola temporal
    misiones_cola = colas_personajes.get(personaje_id, Cola()).a_lista() if personaje_id in colas_personajes else []
    
    return {
        "personaje": personaje.a_diccionario(),
        "misiones": [mision.a_diccionario() for mision in misiones_cola]  # Mostramos la cola temporal
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