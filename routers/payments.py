from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_db, get_current_user
import models, schemas, crud

router = APIRouter(prefix="/pagos", tags=["Pagos"])


# ✅ Registrar pago
@router.post("/", response_model=schemas.PagoResponse)
def registrar_pago(
    pago: schemas.PagoCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    # ✅ Validar Cliente
    cliente = db.query(models.Cliente).filter(models.Cliente.id == pago.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # ✅ Validar Préstamo
    prestamo = db.query(models.Prestamo).filter(models.Prestamo.id == pago.prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    # ✅ Validaciones integradas en el crud
    nuevo_pago = crud.crear_pago(db, pago)

    return nuevo_pago


# ✅ Listar todos los pagos
@router.get("/", response_model=list[schemas.PagoResponse])
def listar_pagos(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return db.query(models.Pago).all()


# ✅ Pagos por Cliente
@router.get("/cliente/{cliente_id}", response_model=list[schemas.PagoResponse])
def pagos_por_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    pagos = db.query(models.Pago).filter(models.Pago.cliente_id == cliente_id).all()
    if not pagos:
        raise HTTPException(status_code=404, detail="No hay pagos para este cliente")
    return pagos


# ✅ Pagos por Préstamo
@router.get("/prestamo/{prestamo_id}", response_model=list[schemas.PagoResponse])
def pagos_por_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    pagos = db.query(models.Pago).filter(models.Pago.prestamo_id == prestamo_id).all()
    if not pagos:
        raise HTTPException(status_code=404, detail="No hay pagos para este préstamo")
    return pagos


# ✅ PAGINAR pagos
@router.get("/paginar")
def paginar_pagos(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page y limit deben ser mayores a 0")

    inicio = (page - 1) * limit

    pagos = db.query(models.Pago).offset(inicio).limit(limit).all()
    total = db.query(models.Pago).count()

    return {
        "pagina": page,
        "por_pagina": limit,
        "total_registros": total,
        "total_paginas": (total + limit - 1) // limit,
        "data": pagos
    }
