from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import date

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    telefono = Column(String(20))
    correo = Column(String(100))
    direccion = Column(String(150))
    monto = Column(Float, nullable=False)
    fecha = Column(Date)
    estado = Column(String(50), default="Activo")

    prestamos = relationship("Prestamo", back_populates="cliente", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="cliente", cascade="all, delete-orphan")  # ✅ agregado


class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    monto_inicial = Column(Float)
    total_interes = Column(Float, default=0)  # ✅ agregado default
    monto_pagado = Column(Float, default=0)
    monto_restante = Column(Float, default=0)
    estado = Column(String(20), default="Activo")
    fecha_inicio = Column(Date, default=date.today)
    fecha_limite = Column(Date)

    cliente = relationship("Cliente", back_populates="prestamos")
    pagos = relationship("Pago", back_populates="prestamo", cascade="all, delete-orphan")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    prestamo_id = Column(Integer, ForeignKey("prestamos.id"), nullable=False)
    monto_pagado = Column(Float, nullable=False)
    fecha_pago = Column(Date, nullable=False)
    estado = Column(String(50), default="Completado")

    cliente = relationship("Cliente", back_populates="pagos")  # ✅ mejorado
    prestamo = relationship("Prestamo", back_populates="pagos")
