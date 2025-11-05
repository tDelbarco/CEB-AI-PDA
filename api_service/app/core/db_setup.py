from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from .config import settings 
from .db_base import Base 

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Creación del Motor (Engine)
ENGINE = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

# Fábrica de Sesiones (SessionLocal)
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
        yield db
    finally:
        db.close()
