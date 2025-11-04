from pydantic import BaseModel
from datetime import date
from typing import Optional

# -----------------------
#   CLIENTES
# -----------------------
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


# -----------------------
#   PRESTAMOS
# -----------------------
class PrestamoBase(BaseModel):
    cliente_id: int
    monto_inicial: float
    total_interes: float = 0
    estado: str = "Activo"

class PrestamoCreate(PrestamoBase):
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None

class PrestamoUpdate(BaseModel):
    estado: Optional[str] = None
    total_interes: Optional[float] = None
    fecha_limite: Optional[date] = None

class Prestamo(PrestamoBase):
    id: int
    fecha_inicio: date
    fecha_limite: date
    monto_pagado: float
    monto_restante: float
    class Config:
        from_attributes = True


# -----------------------
#   PAGOS
# -----------------------
class PagoBase(BaseModel):
    cliente_id: int
    prestamo_id: int
    monto_pagado: float
    fecha_pago: date
    estado: str = "Completado"

class PagoCreate(PagoBase):
    pass

class PagoResponse(PagoBase):
    id: int
    class Config:
        from_attributes = True
