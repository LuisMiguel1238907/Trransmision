from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import SessionLocal
from models import Cliente
from pydantic import BaseModel
from datetime import date
from typing import List, Optional, Dict, Any
from auth import get_current_user

router = APIRouter(prefix="/clientes", tags=["Clientes"])


class ClienteBase(BaseModel):
    nombre: str
    cedula: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    monto: float
    fecha: date
    estado: Optional[str] = "Activo"


class ClienteOut(ClienteBase):
    id: int
    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Crear cliente
@router.post("/", response_model=ClienteOut)
def crear_cliente(
    cliente: ClienteBase,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    if db.query(Cliente).filter(Cliente.cedula == cliente.cedula).first():
        raise HTTPException(status_code=400, detail="Ya existe un cliente con esa cédula")
    
    nuevo_cliente = Cliente(**cliente.dict())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente


# ✅ Listar clientes
@router.get("/", response_model=List[ClienteOut])
def listar_clientes(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return db.query(Cliente).all()


# ✅ Obtener cliente por ID
@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


# ✅ Actualizar cliente
@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(
    cliente_id: int,
    datos: ClienteBase,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if db.query(Cliente).filter(Cliente.cedula == datos.cedula, Cliente.id != cliente_id).first():
        raise HTTPException(status_code=400, detail="La cédula ya pertenece a otro cliente")

    for key, value in datos.dict().items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente


# ✅ Eliminar cliente
@router.delete("/{cliente_id}")
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(cliente)
    db.commit()
    return {"mensaje": "Cliente eliminado correctamente ✅"}


# ✅ Buscar cliente
@router.get("/buscar", response_model=List[ClienteOut])
def buscar_clientes(
    query: str,
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user)
):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Debe ingresar un texto de búsqueda")

    resultados = db.query(Cliente).filter(
        or_(
            Cliente.nombre.like(f"%{query}%"),
            Cliente.cedula.like(f"%{query}%"),
            Cliente.telefono.like(f"%{query}%"),
            Cliente.correo.like(f"%{query}%")
        )
    ).all()

    return resultados


# ✅ Paginación con respuesta tipada
@router.get("/paginar")
def paginar_clientes(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
) -> Dict[str, Any]:

    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page y limit deben ser mayores a 0")

    inicio = (page - 1) * limit

    clientes = db.query(Cliente).offset(inicio).limit(limit).all()
    total = db.query(Cliente).count()

    return {
        "pagina": page,
        "por_pagina": limit,
        "total_registros": total,
        "total_paginas": (total + limit - 1) // limit,
        "data": clientes
    }
