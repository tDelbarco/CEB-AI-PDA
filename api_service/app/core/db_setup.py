from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
# Importamos settings para obtener la URL de la DB
from .config import settings 
# Importamos la Base declarativa del archivo nuevo para evitar la importación circular
from .db_base import Base 

# La URL de la DB debe ser del formato: 
# postgresql://usuario:contraseña@host:puerto/nombre_db
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 1. Creación del Motor (Engine)
# Se usa un pool de conexiones para manejar múltiples solicitudes de FastAPI eficientemente.
ENGINE = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

# 2. Fábrica de Sesiones (SessionLocal)
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,   
    bind=ENGINE        
)

# --- Funciones de Orquestación ---

def init_db_tables():
    """
    Crea las tablas en la DB si no existen.
    Esta función es llamada por @app.on_event("startup") en main.py.
    """
    # IMPORTACIÓN LOCAL: Importamos los modelos aquí dentro para que
    # Base conozca las tablas, pero SIN causar la circularidad al inicio.
    from ..models import user_models 

    print("Verificando y creando tablas de PostgreSQL si es necesario...")
    # Base.metadata.create_all es un comando IDEMPOTENTE: solo crea las tablas que faltan.
    Base.metadata.create_all(bind=ENGINE)
    print("Tablas de DB aseguradas.")

# --- Inyección de Dependencia (Función Generadora) ---

def get_db() -> Generator[SessionLocal, None, None]:
    """
    Generador de dependencias para FastAPI.
    Crea una sesión de DB por solicitud y la cierra automáticamente.
    """
    db = SessionLocal()
    try:
        yield db # Entrega el objeto de sesión al endpoint
    finally:
        # Cierra la conexión después de que se ha terminado de usar
        db.close()
