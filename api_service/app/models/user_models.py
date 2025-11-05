from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..core.db_base import Base 

# ----------------- A. Modelos ORM/DB (Definición de Tablas PostgreSQL) -----------------

class User(Base):
    """Tabla 'usuarios': Almacena los metadatos de la cuenta."""
    __tablename__ = "usuarios"

    # Clave Primaria (PK) - Usamos String para UUIDs
    id_usuario = Column(String, primary_key=True, index=True) 
    
    nombre_usuario = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True) # Opcional, para vinculación
    timestamp_creacion = Column(DateTime, default=datetime.utcnow)

    # Relación: Un usuario puede tener múltiples sesiones/dispositivos
    sesiones = relationship("DeviceSession", back_populates="usuario", cascade="all, delete-orphan")
    # Relación: Un usuario puede participar en múltiples extensiones
    extensiones = relationship("Extension", back_populates="usuario", cascade="all, delete-orphan")

class DeviceSession(Base):
    """Tabla 'dispositivos_sesiones': Almacena los tokens de acceso por dispositivo."""
    __tablename__ = "dispositivos_sesiones"

    # Clave Primaria (PK) - El token es el identificador único de la sesión
    token_sesion = Column(String, primary_key=True, index=True) 

    # Referencia a la tabla 'usuarios'
    id_usuario_fk = Column(String, ForeignKey("usuarios.id_usuario"))
    
    nombre_dispositivo = Column(String, nullable=True)
    timestamp_ultima_actividad = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True) # Clave de revocación (True = activo, False = revocado)

    # Relación: La sesión pertenece a un solo usuario
    usuario = relationship("User", back_populates="sesiones")


# ----------------- B. Esquemas Pydantic (API Input/Output) -----------------

# --- Esquemas de Entrada (Input) ---

class SessionCreate(BaseModel):
    """Esquema para la primera visita/creación de sesión."""
    # El frontend debe enviar un nombre o tipo de dispositivo (ej. 'iPhone 15', 'Chrome Desktop')
    nombre_dispositivo: str = Field(..., max_length=100, description="Identificador del dispositivo/navegador.")

class UserEmailLink(BaseModel):
    """Esquema para solicitar el vínculo o recuperación por email."""
    email: EmailStr

# --- Esquemas de Salida (Output) ---

class SessionDetails(BaseModel):
    """Detalles internos de una sesión de dispositivo (para el perfil del usuario)."""
    token_sesion: str
    nombre_dispositivo: str
    timestamp_ultima_actividad: datetime
    activo: bool
    
    class Config:
        from_attributes = True

class UserPublic(BaseModel):
    """Datos del usuario que se exponen públicamente (ej. después de un login exitoso)."""
    id_usuario: str
    nombre_usuario: str
    email: Optional[EmailStr] = None # Puede ser nulo
    
    # Para incluir las sesiones en la salida
    sesiones: list[SessionDetails] = []

    class Config:
        from_attributes = True