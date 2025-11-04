from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Parámetros de conexión
MYSQL_USER = "root"
MYSQL_PASSWORD = "root123"  # cámbiala si es diferente
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DB = "backend_db"

# URL de conexión
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa
Base = declarative_base()
