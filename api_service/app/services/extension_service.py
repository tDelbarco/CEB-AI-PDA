import asyncio
from typing import Optional, Dict
from sqlalchemy.orm import Session
import io
import zipfile

from ..core import gemini_client
from ..crud import crud_extension
from ..models.extension_models import Extension
from ..core.db_setup import SessionLocal 
from . import extension_utils

# Constante para indicar un ZIP fallido o un error en el código_generado
ERROR_CODE = "GENERATION_FAILED"

def process_and_save_extension(
    extension_id: str, 
    prompt: str, 
    funcionalidades: Optional[str] = None, 
    identificadores: Optional[str] = None, 
    zip_bytes: Optional[bytes] = None
):
    """
    Función síncrona que ejecuta la tarea en segundo plano: 
    llama a la IA, procesa la respuesta y guarda el código generado.
    
    Recibe los bytes del ZIP y los convierte a texto de referencia.
    """
    
    db: Session = SessionLocal()
    codigo_referencia: Optional[str] = None
    
    # Obtener la extensión para poder actualizar su estado en caso de error
    extension = db.query(Extension).filter(Extension.id_extension == extension_id).first()
    if not extension:
        print(f"Error fatal: Extensión {extension_id} no encontrada en la DB.")
        db.close()
        return

    try:
        if zip_bytes:
            try:
                codigo_referencia = extension_utils.zip_a_texto(zip_bytes)
                print(f"ZIP de referencia procesado a texto para extensión {extension_id}")
            except ValueError as e:
                crud_extension.update_generated_code(db, extension, ERROR_CODE + f": Error al procesar ZIP: {str(e)}")
                db.close()
                return

        # Llamar a la IA para obtener el código estructurado (asíncrona)
        structured_response = asyncio.run(
            gemini_client.generate_extension_code(
                prompt_principal=prompt,
                funcionalidades=funcionalidades,
                identificadores=identificadores,
                codigo_referencia=codigo_referencia
            )
        )

        if not structured_response:
            # Fallo en la llamada a la API
            crud_extension.update_generated_code(db, extension, ERROR_CODE + ": API fallida o respuesta vacía.")
            db.close()
            return

        # Analizar la respuesta estructurada
        file_dict: Dict[str, str] = extension_utils.parse_gemini_response(structured_response)
        
        if not file_dict or "manifest.json" not in file_dict:
            # Fallo en el análisis (formato incorrecto de Gemini)
            # Guardamos la respuesta cruda para depuración
            crud_extension.update_generated_code(db, extension, ERROR_CODE + ": Formato de salida incorrecto. Respuesta: " + structured_response[:200])
            db.close()
            return

        # Generar el archivo ZIP binario en memoria
        zip_bytes_generated = extension_utils.create_zip_from_files(file_dict)
        
        # Actualizar el registro en la DB con el código completo (para depuración)
        extension_text = structured_response 
        crud_extension.update_generated_code(db, extension, extension_text)
        

        print(f"Extensión {extension_id} generada, procesada y código/ZIP guardado.")
            
    except Exception as e:
        print(f"Excepción al procesar la extensión {extension_id}: {e}")
        # Reportar el error en la DB
        crud_extension.update_generated_code(db, extension, ERROR_CODE + f": Error interno del servicio: {str(e)[:50]}")
            
    finally:
        db.close()