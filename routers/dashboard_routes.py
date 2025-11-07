from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from datetime import date
from auth import get_db, get_current_user
import models

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ✅ 1. Resumen General (Tarjetas superiores)
@router.get("/resumen")
def dashboard_resumen(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    total_clientes = db.query(models.Cliente).count()
    total_prestamos = db.query(models.Prestamo).count()

    prestamos_activos = db.query(models.Prestamo).filter(models.Prestamo.estado == "Activo").count()
    prestamos_pagados = db.query(models.Prestamo).filter(models.Prestamo.estado == "Pagado").count()
    prestamos_atrasados = db.query(models.Prestamo).filter(models.Prestamo.estado == "Atrasado").count()

    # ✅ SUMA REAL de los intereses pactados para la tarjeta de ganancias
    ganancias_interes = db.query(func.sum(models.Prestamo.total_interes)).scalar()
    if ganancias_interes is None:
        ganancias_interes = 0

    return {
        "total_clientes": total_clientes,
        "total_prestamos": total_prestamos,
        "prestamos_activos": prestamos_activos,
        "prestamos_pagados": prestamos_pagados,
        "prestamos_atrasados": prestamos_atrasados,
        "ganancias_interes": float(ganancias_interes),

        "por_estado": {
            "Activo": prestamos_activos,
            "Pagado": prestamos_pagados,
            "Atrasado": prestamos_atrasados
        }
    }


# ✅ 2. Pagos por mes (para gráfica)
@router.get("/pagos-mes")
def pagos_por_mes(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    pagos_mes = db.query(
        extract('month', models.Pago.fecha_pago).label("mes"),
        func.count(models.Pago.id)
    ).group_by("mes").all()

    resultado = {mes: 0 for mes in range(1, 13)}
    for mes_db, cantidad in pagos_mes:
        resultado[int(mes_db)] = cantidad

    return [{"mes": m, "cantidad": resultado[m]} for m in range(1, 13)]


# ✅ 3. Tabla de resumen de préstamos
@router.get("/resumen-prestamos")
def resumen_prestamos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    prestamos = db.query(models.Prestamo).all()

    data = []
    for p in prestamos:
        data.append({
            "prestamo_id": p.id,
            "cliente": p.cliente.nombre if p.cliente else "Sin cliente",
            "monto_total": p.monto_inicial + p.total_interes,
            "pagado": p.monto_pagado,
            "restante": p.monto_restante,
            "estado": p.estado,
            "fecha_limite": p.fecha_limite
        })

    return {"data": data, "total": len(data)}


# ✅ 4. Reporte general con filtros
@router.get("/reporte")
def reporte_general(
    mes: int | None = None,
    anio: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if mes and (mes < 1 or mes > 12):
        raise HTTPException(status_code=400, detail="El mes debe estar entre 1 y 12")

    pagos_query = db.query(models.Pago)

    if mes:
        pagos_query = pagos_query.filter(extract('month', models.Pago.fecha_pago) == mes)

    if anio:
        pagos_query = pagos_query.filter(extract('year', models.Pago.fecha_pago) == anio)

    pagos = pagos_query.all()

    total_prestamos = db.query(models.Prestamo).count()
    total_pagado = sum(p.monto_pagado for p in pagos)
    clientes_activos = db.query(models.Prestamo).filter(models.Prestamo.estado == "Activo").count()

    resumen_estados = {
        "Pagados": db.query(models.Prestamo).filter(models.Prestamo.estado == "Pagado").count(),
        "Activos": db.query(models.Prestamo).filter(models.Prestamo.estado == "Activo").count(),
        "Atrasados": db.query(models.Prestamo).filter(models.Prestamo.estado == "Atrasado").count()
    }

    pagos_mes = db.query(
        extract('month', models.Pago.fecha_pago).label("mes"),
        func.count(models.Pago.id)
    ).group_by("mes").all()

    pagos_mensuales = {m: 0 for m in range(1, 13)}
    for mes_db, cantidad in pagos_mes:
        pagos_mensuales[int(mes_db)] = cantidad

    return {
        "total_prestamos": total_prestamos,
        "total_pagado": total_pagado,
        "intereses_generados": total_pagado,
        "clientes_activos": clientes_activos,
        "estado_prestamos": resumen_estados,
        "pagos_por_mes": pagos_mensuales
    }
