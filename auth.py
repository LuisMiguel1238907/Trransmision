from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Usuario

# Configuración JWT
SECRET_KEY = "super_secret_key_cambiala_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Para encriptar contraseñas
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Encriptar contraseña
def hash_password(password):
    print("✅ Contraseña recibida:", password, type(password))
    password = str(password)[:72]
    return pwd_context.hash(password)


    # recortar a 72 caracteres para evitar error bcrypt
    password = password[:72]


# Verificar contraseña

def verify_password(password: str, hashed: str):
    password = str(password)
    password = password[:72]
    return pwd_context.verify(password, hashed)


# Crear JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Obtener usuario autenticado desde token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user
