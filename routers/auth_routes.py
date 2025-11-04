from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import hash_password, verify_password, create_access_token, get_db, get_current_user
from models import Usuario
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# ✅ MODELOS Pydantic
class UserRegister(BaseModel):
    nombre: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ✅ Modelo para actualización (password opcional)
class UserUpdate(BaseModel):
    nombre: str
    email: str
    password: Optional[str] = None


# ✅ Registro de usuarios
@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    user_db = db.query(Usuario).filter(Usuario.email == user.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo_usuario = Usuario(
        nombre=user.nombre,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": "Usuario creado exitosamente"}


# ✅ Login
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_db = db.query(Usuario).filter(Usuario.email == user.email).first()
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    token = create_access_token({"sub": str(user_db.id)})
    return {"access_token": token, "token_type": "bearer"}


# ✅ Obtener usuario actual
@router.get("/me")
def leer_usuario_actual(usuario: Usuario = Depends(get_current_user)):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email
    }


# ✅ Actualizar información del usuario
@router.put("/update")
def actualizar_usuario(data: UserUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    usuario = db.query(Usuario).filter(Usuario.id == user.id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = data.nombre
    usuario.email = data.email

    # ✅ Solo actualizar contraseña si se envía
    if data.password and data.password.strip() != "":
        usuario.password = hash_password(data.password)

    db.commit()
    return {"mensaje": "Usuario actualizado correctamente"}
