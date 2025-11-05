from sqlalchemy.orm import Session
from datetime import datetime
import uuid 
from typing import List
from ..models.extension_models import Extension, ExtensionCreate
from ..models.user_models import User 


# ----------------- Funciones de Extensión -----------------

def create_extension(db: Session, user_id: str, extension_in: ExtensionCreate) -> Extension:
    """
    Crea un nuevo registro de extensión asociado a un usuario.
    """
    new_id = str(uuid.uuid4())
    
    db_extension = Extension(
        id_extension=new_id,
        id_usuario_fk=user_id,
        nombre=extension_in.nombre,
        prompt_original=extension_in.prompt_original,
        timestamp_creacion=datetime.utcnow(),
        # codigo_generado se deja nulo hasta que la IA lo complete
    )
    
    db.add(db_extension)
    db.commit()
    db.refresh(db_extension)
    
    return db_extension

def get_user_extension_by_id(db: Session, user_id: str, extension_id: str) -> Extension | None:
    """Obtiene una extensión específica por ID, asegurando que pertenezca al usuario."""
    return db.query(Extension).filter(
        Extension.id_extension == extension_id,
        Extension.id_usuario_fk == user_id
    ).first()

def get_all_user_extensions(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Extension]:
    """Obtiene todas las extensiones creadas por un usuario."""
    return db.query(Extension).filter(Extension.id_usuario_fk == user_id).offset(skip).limit(limit).all()

def update_generated_code(db: Session, extension: Extension, generated_code: str) -> Extension:
    """Actualiza el campo codigo_generado de una extensión existente."""
    extension.codigo_generado = generated_code
    extension.timestamp_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(extension)
    return extension