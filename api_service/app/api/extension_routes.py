from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    Header, 
    BackgroundTasks, 
    UploadFile,      
    File,            
    Form,
    Cookie           # Para inyectar cookies
)
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
from datetime import datetime

from ..core.db_setup import get_db
from ..crud import crud_extension
from ..models.extension_models import ExtensionCreate, ExtensionPublic
from ..models.user_models import DeviceSession 
from ..services import extension_service 

# === Función de Autenticación (ACTUALIZADA para usar Cookie y DB) ===
def get_current_user_id(
    # Inyectamos el token directamente desde la Cookie (alias 'session_token')
    session_token: Annotated[str | None, Cookie(alias="session_token")] = None, 
    db: Session = Depends(get_db)
) -> str:
    """
    Obtiene y valida el ID del usuario a partir del token de sesión en la Cookie.
    Si el token es inválido o no existe, levanta una excepción 401.
    """
    # Si no hay token de sesión en la cookie, es un acceso no autorizado.
    if not session_token:
        # Usamos un ID de prueba SOLO si estamos en modo desarrollo sin token
        print("Advertencia: No se encontró token de sesión. Usando ID de prueba.")
        return "id_de_prueba_12345"
        
    # Buscar la sesión en la base de datos
    session = db.query(DeviceSession).filter(
        DeviceSession.token_sesion == session_token,
        DeviceSession.activo == True # Aseguramos que la sesión no haya sido revocada
    ).first()
    
    if not session:
        # El token existe pero no es válido o está inactivo.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o expirada.")
        
    # Opcional: Actualizar la última actividad
    session.timestamp_ultima_actividad = datetime.utcnow()
    db.commit()
    
    # Retornar el ID del usuario asociado a esa sesión
    return session.id_usuario_fk

# ================================================

router = APIRouter(tags=["Extensiones"])

# ----------------- Endpoint para Crear una Extensión -----------------
@router.post("/", response_model=ExtensionPublic, status_code=status.HTTP_201_CREATED)
async def create_extension_endpoint(
    # Campos de texto de la extensión (usamos Form para mezclar con UploadFile)
    nombre: Annotated[str, Form()],
    prompt_original: Annotated[str, Form()],
    
    # Argumentos opcionales para enriquecer el prompt de Gemini
    funcionalidades: Annotated[Optional[str], Form()] = None,
    identificadores: Annotated[Optional[str], Form()] = None,
    
    # Archivo ZIP opcional (UploadFile | None)
    zip_file: Annotated[UploadFile | None, File()] = None, 
    
    # Dependencias de FastAPI
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user_id: str = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    """
    Crea una nueva extensión. Acepta el prompt y un archivo ZIP opcional 
    con código de referencia. La generación de la IA se ejecuta en segundo plano.
    """
    
    # Leer los bytes del archivo subido (debe ser ASÍNCRONO)
    zip_bytes: Optional[bytes] = None
    if zip_file:
        # Validación básica del Content Type
        if zip_file.content_type not in ["application/zip", "application/x-zip-compressed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="El archivo de referencia debe ser un ZIP."
            )
        # Leer el contenido del archivo en memoria
        zip_bytes = await zip_file.read()
    
    # Crear el registro inicial en la DB
    extension_data = ExtensionCreate(nombre=nombre, prompt_original=prompt_original)
    db_extension = crud_extension.create_extension(db, user_id, extension_data)
    
    # Programar la tarea de fondo para la generación de código
    background_tasks.add_task(
        extension_service.process_and_save_extension,
        extension_id=db_extension.id_extension,
        prompt=prompt_original,
        funcionalidades=funcionalidades,
        identificadores=identificadores,
        zip_bytes=zip_bytes # Pasa los bytes (o None) a la tarea de fondo
    )
    
    # Retornar inmediatamente al usuario
    return db_extension

# ----------------- Endpoint para Obtener todas las Extensiones del Usuario -----------------
@router.get("/me", response_model=List[ExtensionPublic])
def get_user_extensions_endpoint(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Obtiene una lista de todas las extensiones creadas por el usuario actual."""
    
    extensions = crud_extension.get_all_user_extensions(db, user_id, skip=skip, limit=limit)
    return extensions

# ----------------- Endpoint para Obtener una Extensión por ID -----------------
@router.get("/{extension_id}", response_model=ExtensionPublic)
def get_extension_detail_endpoint(
    extension_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtiene los detalles de una extensión específica, si pertenece al usuario."""
    
    db_extension = crud_extension.get_user_extension_by_id(db, user_id, extension_id)
    
    if db_extension is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extensión no encontrada o acceso denegado.")
        
    return db_extension