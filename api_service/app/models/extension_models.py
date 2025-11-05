from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..core.db_base import Base 


# ----------------- A. Modelos ORM/DB (Definición de Tablas PostgreSQL) -----------------

class Extension(Base):
    """Tabla 'extensiones': Almacena los metadatos y el código de las extensiones generadas."""
    __tablename__ = "extensiones"

    # Clave Primaria (PK)
    id_extension = Column(String, primary_key=True, index=True) 
    
    # Clave Foránea (FK)
    id_usuario_fk = Column(String, ForeignKey("usuarios.id_usuario"))

    # Datos de la Extensión
    nombre = Column(String, index=True)
    prompt_original = Column(Text, nullable=False) # Usar Text para prompts largos
    codigo_generado = Column(Text, nullable=True)  # El código generado (puede ser nulo al inicio)
    
    timestamp_creacion = Column(DateTime, default=datetime.utcnow)
    timestamp_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación: La extensión pertenece a un solo usuario
    usuario = relationship("User", back_populates="extensiones")

# ----------------- B. Esquemas Pydantic (API Input/Output) -----------------

# Esquema para crear una extensión (Input)
class ExtensionCreate(BaseModel):
    nombre: str = Field(..., max_length=150)
    prompt_original: str = Field(..., description="El prompt o descripción para generar la extensión.")

# Esquema de Salida (Output)
class ExtensionPublic(BaseModel):
    id_extension: str
    nombre: str
    prompt_original: str
    codigo_generado: Optional[str] = None # Opcional porque puede ser generado después
    timestamp_creacion: datetime
    
    class Config:
        from_attributes = True