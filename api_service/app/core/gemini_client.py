import asyncio
import os
import google.generativeai as genai
from typing import Optional
from .config import settings

# Configuración del cliente Gemini
if settings.GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Seleccionamos el modelo
model = genai.GenerativeModel("gemini-2.5-flash")

async def generate_extension_code(
    prompt_principal: str, 
    funcionalidades: Optional[str] = None, 
    identificadores: Optional[str] = None, 
    codigo_referencia: Optional[str] = None
) -> Optional[str]:
    """
    Función asíncrona que llama al modelo de Gemini.
    Retorna la respuesta de texto con el código estructurado o None.
    """
    
    # Estructuramos el mensaje que se le enviará al modelo (TU LÓGICA)
    mensaje = f"""
    Eres un generador de extensiones de Google Chrome. 
    Debes crear una extensión completamente funcional en base a las siguientes instrucciones.
    
    --- Instrucciones ---
    {prompt_principal.strip()}
    
    --- Funcionalidades requeridas ---
    {funcionalidades if funcionalidades else 'No se especificaron funcionalidades adicionales.'}
    
    --- Identificadores o clases relevantes ---
    {identificadores if identificadores else 'No se especificaron identificadores o clases relevantes.'}
    
    --- Código de referencia ---
    {codigo_referencia if codigo_referencia else 'No se adjuntó código de referencia.'}
    
    --- Formato de salida ---
    Devuelve únicamente el código fuente de la extensión, **sin explicaciones ni texto adicional**,
    en el siguiente formato exacto (respetar guiones y estructura):
    
    --- archivo: manifest.json ---
    (contenido del archivo)
    --- fin archivo ---
    
    --- archivo: background.js ---
    (contenido del archivo)
    --- fin archivo ---
    
    --- archivo: popup.html ---
    (contenido del archivo)
    --- fin archivo ---
    
    Cada archivo debe incluir su contenido completo y funcional.
    No incluyas texto fuera de estos bloques ni encabezados adicionales.
    """

    try:
        loop = asyncio.get_event_loop()
        respuesta = await loop.run_in_executor(None, lambda: model.generate_content(mensaje))
        
        return respuesta.text
    
    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        return None