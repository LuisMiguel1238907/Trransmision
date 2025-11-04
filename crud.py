from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date, timedelta
from models import Cliente, Prestamo, Pago
import schemas

# ✅ CREAR CLIENTE
def crear_cliente(db: Session, cliente: schemas.ClienteCreate):
    nuevo_cliente = Cliente(**cliente.dict())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente


# ✅ LISTAR CLIENTES
def obtener_clientes(db: Session):
    return db.query(Cliente).all()


# ✅ OBTENER CLIENTE POR ID
def obtener_cliente_por_id(db: Session, cliente_id: int):
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()


# ✅ ACTUALIZAR CLIENTE
def actualizar_cliente(db: Session, cliente_id: int, datos_actualizados: schemas.ClienteCreate):
    cliente = obtener_cliente_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for key, value in datos_actualizados.dict().items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente


# ✅ ELIMINAR CLIENTE
def eliminar_cliente(db: Session, cliente_id: int):
    cliente = obtener_cliente_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(cliente)
    db.commit()
    return {"mensaje": "Cliente eliminado exitosamente"}


# ✅ CREAR PRÉSTAMO
def crear_prestamo(db: Session, prestamo: schemas.PrestamoCreate):

    # ✅ Verificar si el cliente existe
    cliente = obtener_cliente_por_id(db, prestamo.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no existe")

    # ✅ El cliente no puede tener otro préstamo activo
    prestamo_activo = db.query(Prestamo).filter(
        Prestamo.cliente_id == prestamo.cliente_id,
        Prestamo.estado == "Activo"
    ).first()

    if prestamo_activo:
        raise HTTPException(
            status_code=400,
            detail="El cliente ya tiene un préstamo activo"
        )

    # ✅ Validaciones de valores
    if prestamo.monto_inicial <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")

    if prestamo.total_interes < 0:
        raise HTTPException(status_code=400, detail="El interés no puede ser negativo")

    # ✅ Manejo de fechas
    fecha_inicio = prestamo.fecha_inicio or date.today()
    fecha_limite = prestamo.fecha_limite or (fecha_inicio + timedelta(days=30))

    # ✅ Crear préstamo
    nuevo_prestamo = Prestamo(
        cliente_id=prestamo.cliente_id,
        monto_inicial=prestamo.monto_inicial,
        total_interes=prestamo.total_interes,
        fecha_inicio=fecha_inicio,
        fecha_limite=fecha_limite,
        monto_pagado=0,
        monto_restante=prestamo.monto_inicial + prestamo.total_interes,
        estado="Activo"
    )

    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)
    return nuevo_prestamo


# ✅ LISTAR PRÉSTAMOS
def listar_prestamos(db: Session):
    return db.query(Prestamo).all()


# ✅ OBTENER PRÉSTAMO
def obtener_prestamo(db: Session, prestamo_id: int):
    return db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()


# ✅ ACTUALIZAR PRÉSTAMO
def actualizar_prestamo(db: Session, prestamo_id: int, data: schemas.PrestamoUpdate):
    prestamo = obtener_prestamo(db, prestamo_id)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(prestamo, key, value)

    db.commit()
    db.refresh(prestamo)
    return prestamo


# ✅ ELIMINAR PRÉSTAMO
def eliminar_prestamo(db: Session, prestamo_id: int):
    prestamo = obtener_prestamo(db, prestamo_id)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    db.delete(prestamo)
    db.commit()
    return {"mensaje": "Préstamo eliminado exitosamente"}


# ✅ CREAR PAGO
def crear_pago(db: Session, pago: schemas.PagoCreate):

    # ✅ Validar cliente existe
    cliente = obtener_cliente_por_id(db, pago.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # ✅ Validar préstamo existe
    prestamo = obtener_prestamo(db, pago.prestamo_id)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    # ✅ Validar monto
    if pago.monto_pagado <= 0:
        raise HTTPException(status_code=400, detail="El monto pagado debe ser mayor a 0")

    # ✅ Evitar pagos a préstamos pagados
    if prestamo.estado == "Pagado":
        raise HTTPException(status_code=400, detail="Este préstamo ya está pagado")

    # ✅ Evitar excedentes
    if pago.monto_pagado > prestamo.monto_restante:
        raise HTTPException(
            status_code=400,
            detail=f"El pago supera el saldo restante. Saldo: {prestamo.monto_restante}"
        )

    # ✅ Registrar pago (si no mandan fecha, usar hoy)
    fecha_pago = pago.fecha_pago or date.today()

    nuevo_pago = Pago(
        cliente_id=pago.cliente_id,
        prestamo_id=pago.prestamo_id,
        monto_pagado=pago.monto_pagado,
        fecha_pago=fecha_pago,
        estado="Completado"
    )

    db.add(nuevo_pago)

    # ✅ Actualizar préstamo
    prestamo.monto_pagado += pago.monto_pagado
    prestamo.monto_restante = (prestamo.monto_inicial + prestamo.total_interes) - prestamo.monto_pagado

    # ✅ Estado según saldo
    if prestamo.monto_restante <= 0:
        prestamo.estado = "Pagado"
    elif date.today() > prestamo.fecha_limite:
        prestamo.estado = "Atrasado"
    else:
        prestamo.estado = "Activo"

    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago
