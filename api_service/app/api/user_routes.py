from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from ..core.db_setup import get_db
from ..crud import crud_user # Importa las funciones de lógica
from ..models.user_models import SessionCreate, UserPublic

router = APIRouter()

# ----------------- Endpoint para Crear Sesión/Usuario (Primera Visita) -----------------

@router.post("/session", response_model=UserPublic)
def create_session_and_user(
    session_data: SessionCreate, # Pydantic valida el JSON de entrada
    response: Response,          # Para manejar las cookies
    db: Session = Depends(get_db) # Inyección de la sesión DB
):
    """Crea un nuevo usuario genérico y establece el token de sesión en una cookie."""
    
    # Crea el usuario y la sesión/token
    user, token = crud_user.create_initial_user_and_session(db, session_data)
    
    # Establece el token en una cookie persistente
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,        # No accesible por JS (seguridad)
        max_age=31536000,     # Persistente por un año
        samesite="Lax"        # Configuración de seguridad
    )
    
    # Retorna los datos públicos del usuario
    return user


# ----------------- Endpoint para Revocación de Sesiones -----------------

@router.post("/session/revoke")
def revoke_device_session(
    token_a_revocar: str, # Se podría pasar el token a revocar
    db: Session = Depends(get_db)
):
    """Invalida un token de sesión específico (para desvincular un dispositivo remotamente)."""
    
    if crud_user.revoke_session(db, token_a_revocar):
        return {"message": "Sesión revocada exitosamente."}
    
    raise HTTPException(status_code=404, detail="Token de sesión no encontrado o ya inactivo.")


# ----------------- Endpoint para Obtener Usuario (Verificación del Token) -----------------

@router.get("/me", response_model=UserPublic)
def get_current_user_data(
    # Nota: Aquí deberías extraer el token de la cookie de la solicitud (Request)
    # Por simplicidad, asumimos que el token es un header o query param
    token: str, 
    db: Session = Depends(get_db)
):
    """Devuelve los datos del usuario actual si el token es válido y activo."""
    
    user = crud_user.get_user_by_token(db, token)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Token no válido o inactivo. Acceso denegado.")
    
    return user