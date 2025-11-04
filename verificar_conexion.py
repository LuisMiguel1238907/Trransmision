from sqlalchemy import create_engine

# Cambia los valores según tu configuración
usuario = "root"
contrasena = "root123"
host = "localhost"
base_datos = "backend_db"

try:
    engine = create_engine(f"mysql+mysqlconnector://{usuario}:{contrasena}@{host}/{base_datos}")
    conexion = engine.connect()
    print("✅ Conexión exitosa a la base de datos")
    conexion.close()
except Exception as e:
    print("❌ Error al conectar:", e)

from database import SessionLocal
from models import Cliente

# Crear una sesión
db = SessionLocal()

# Consultar todos los clientes
clientes = db.query(Cliente).all()

print("\nClientes actualmente en la base de datos:\n")
for cliente in clientes:
    print(f"ID: {cliente.id}, Nombre: {cliente.nombre}, Cédula: {cliente.cedula}, Estado: {cliente.estado}")

db.close()

