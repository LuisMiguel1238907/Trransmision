from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from auth import get_db, get_current_user
import models, schemas, crud

router = APIRouter(prefix="/prestamos", tags=["Prestamos"])

# ✅ Crear préstamo — solo un POST
@router.post("", response_model=schemas.Prestamo)
def crear_prestamo(
    prestamo: schemas.PrestamoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    print("📌 Backend recibe:", prestamo.dict())

    # Saneo
    if not prestamo.fecha_inicio:
        prestamo.fecha_inicio = None

    if not prestamo.fecha_limite:
        prestamo.fecha_limite = None

    return crud.crear_prestamo(db, prestamo)


# ✅ Listar préstamos — solo un GET
@router.get("", response_model=list[schemas.Prestamo])
def listar_prestamos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.listar_prestamos(db)


# ✅ Obtener préstamo por ID
@router.get("/{prestamo_id}", response_model=schemas.Prestamo)
def obtener_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    prestamo = crud.obtener_prestamo(db, prestamo_id)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return prestamo


# ✅ Actualizar préstamo
@router.put("/{prestamo_id}", response_model=schemas.Prestamo)
def actualizar_prestamo(
    prestamo_id: int,
    data: schemas.PrestamoUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if data.fecha_limite == "":
        data.fecha_limite = None

    return crud.actualizar_prestamo(db, prestamo_id, data)


# ✅ Eliminar préstamo
@router.delete("/{prestamo_id}")
def eliminar_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.eliminar_prestamo(db, prestamo_id)


# ✅ Préstamos por cliente
@router.get("/cliente/{cliente_id}", response_model=list[schemas.Prestamo])
def prestamos_por_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return (
        db.query(models.Prestamo)
        .filter(models.Prestamo.cliente_id == cliente_id)
        .all()
    )


# ✅ Verificar atrasados
@router.put("/verificar-atrasados")
def verificar_atrasados(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    hoy = date.today()
    prestamos = db.query(models.Prestamo).all()

    for prestamo in prestamos:
        if prestamo.monto_restante > 0 and prestamo.fecha_limite and prestamo.fecha_limite < hoy:
            prestamo.estado = "Atrasado"

    db.commit()
    return {"mensaje": "Estados actualizados ✅"}


# ✅ Paginación
@router.get("/paginar")
def paginar_prestamos(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="page y limit deben ser mayores a 0"
        )

    inicio = (page - 1) * limit

    prestamos = (
        db.query(models.Prestamo)
        .offset(inicio)
        .limit(limit)
        .all()
    )

    total = db.query(models.Prestamo).count()

    return {
        "pagina": page,
        "por_pagina": limit,
        "total_registros": total,
        "total_paginas": (total + limit - 1) // limit,
        "data": prestamos,
    }
