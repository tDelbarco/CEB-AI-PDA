from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """
    Clase que define todas las variables de configuración de la aplicación.
    Los valores se leen automáticamente del archivo .env o del entorno del sistema.
    """
    
    # ⚙️ Configuración General
    PROJECT_NAME: str = "CEB-AI Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 💾 Configuraciones de la DB (PostgreSQL)
    DATABASE_URL: str = "postgresql://user:password@localhost/ceb_ai_db" # Valor por defecto

    # 🔒 Seguridad y Tokens
    # Clave secreta fuerte y única, esencial para firmar cookies y JWT (si los usas).
    SECRET_KEY: str 
    
    # Variables de la IA
    GEMINI_API_KEY: str

    # 🌐 Configuración de CORS/UI
    # Lista de orígenes permitidos (donde corre el frontend Streamlit/Taipy)
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501", 
        "http://127.0.0.1:8501"
    ] 

    # Configuración de Pydantic para la carga de entorno
    model_config = SettingsConfigDict(
        env_file='.env',      # Indica que cargue variables desde el archivo .env
        extra='ignore'        # Ignora variables en el .env que no estén definidas aquí
    )

# Instancia Global
settings = Settings()