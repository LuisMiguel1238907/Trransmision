from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

# ====================================================
#   CLIENTES
# ====================================================
class ClienteBase(BaseModel):
    nombre: str
    cedula: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    monto: float
    fecha: Optional[date] = None
    estado: Optional[str] = "Activo"

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id: int
    class Config:
        from_attributes = True


# ====================================================
#   PRESTAMOS
# ====================================================
class PrestamoBase(BaseModel):
    cliente_id: int
    monto_inicial: float = Field(..., gt=0)
    total_interes: float = Field(..., ge=0)

class PrestamoCreate(PrestamoBase):
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None
    estado: Optional[str] = "Activo"

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }

class PrestamoUpdate(BaseModel):
    total_interes: Optional[float] = None
    estado: Optional[str] = None
    fecha_limite: Optional[date] = None

class Prestamo(PrestamoBase):
    id: int
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None
    estado: str
    monto_pagado: float
    monto_restante: float
    cliente: Optional[Cliente] = None

    class Config:
        from_attributes = True


# ====================================================
#   PAGOS
# ====================================================
class PagoBase(BaseModel):
    cliente_id: int
    prestamo_id: int
    monto_pagado: float = Field(..., gt=0)
    fecha_pago: Optional[date] = None
    estado: str = "Completado"

class PagoCreate(PagoBase):
    pass

class PagoResponse(PagoBase):
    id: int
    cliente: Optional[Cliente] = None
    prestamo: Optional[Prestamo] = None

    class Config:
        from_attributes = True
