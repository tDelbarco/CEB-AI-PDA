from sqlalchemy.orm import Session
from datetime import datetime
import uuid # Para generar IDs únicos
from ..models.user_models import User, DeviceSession
from ..models.user_models import SessionCreate

# ----------------- Funciones de Usuario -----------------

def create_initial_user_and_session(db: Session, session_data: SessionCreate) -> tuple[User, str]:
    """
    Crea un nuevo usuario genérico y su sesión/token inicial.
    Retorna el objeto User y el nuevo token generado.
    """
    new_user_id = str(uuid.uuid4())
    new_token = str(uuid.uuid4()).replace('-', '') # Ejemplo de token simple
    
    # Crea el usuario (modelo ORM)
    db_user = User(
        id_usuario=new_user_id,
        nombre_usuario=f"User_{new_user_id[:8]}",
        timestamp_creacion=datetime.utcnow()
    )
    db.add(db_user)
    
    # Crea la sesión (modelo ORM)
    db_session = DeviceSession(
        token_sesion=new_token,
        id_usuario_fk=new_user_id,
        nombre_dispositivo=session_data.nombre_dispositivo,
        timestamp_ultima_actividad=datetime.utcnow(),
        activo=True
    )
    db.add(db_session)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user, new_token

def get_user_by_token(db: Session, token: str) -> User | None:
    """Busca un usuario activo a través de su token de sesión."""
    session_record = db.query(DeviceSession).filter(
        DeviceSession.token_sesion == token,
        DeviceSession.activo == True # Solo busca tokens activos
    ).first()

    if session_record:
        # Devuelve el objeto Usuario relacionado con el token encontrado
        return session_record.usuario
    return None

def revoke_session(db: Session, token: str) -> bool:
    """Revoca un token de sesión (lo marca como inactivo)."""
    session_record = db.query(DeviceSession).filter(DeviceSession.token_sesion == token).first()
    
    if session_record:
        session_record.activo = False
        db.commit()
        return True
    return False

# ... (Aquí irían funciones para vincular email, añadir sesión, etc.)
