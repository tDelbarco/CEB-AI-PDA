from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .app.core.config import settings
from .app.core.db_setup import init_db_tables 
from .app.api import user_routes 

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend para CEB-AI: Plataforma de Creación y Colaboración de Extensiones."
)

# Configuración de Middleware (CORS)
# Es vital para que el frontend (Streamlit/Taipy) pueda comunicarse con esta API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Lista de orígenes permitidos desde settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de las Rutas/Endpoints
app.include_router(user_routes.router, prefix=settings.API_V1_STR + "/users", tags=["users"])
# app.include_router(extension_routes.router, prefix=settings.API_V1_STR + "/extensions", tags=["extensions"])


@app.on_event("startup")
def startup_event():
    """Ejecuta tareas críticas como la conexión a la base de datos al inicio."""
    init_db_tables() 
    print(f"CEB-AI API ({settings.VERSION}) iniciada y conectada a la DB.")


@app.get("/")
def read_root():
    """Endpoint para verificar que la API está funcionando."""
    return {"message": "CEB-AI API está funcionando. Revisa /docs para ver la documentación."}
    