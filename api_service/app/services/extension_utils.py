import zipfile
import io
import re
import os
from typing import Dict

# ... (deja las funciones parse_gemini_response y create_zip_from_files iguales) ...
def parse_gemini_response(response_text: str) -> Dict[str, str]:
    """
    Analiza la respuesta estructurada de Gemini y extrae el contenido de cada archivo.
    Retorna un diccionario: {'manifest.json': '...', 'popup.html': '...'}
    """
    
    # Patrón Regex para encontrar los bloques de archivo
    # Busca la estructura: --- archivo: <nombre> --- (...) --- fin archivo ---
    pattern = re.compile(
        r"--- archivo: (.*?) ---\s*\n(.*?)\s*--- fin archivo ---", 
        re.DOTALL | re.IGNORECASE
    )
    
    files: Dict[str, str] = {}
    
    # Encontrar todas las coincidencias
    for match in pattern.finditer(response_text):
        filename = match.group(1).strip()
        content = match.group(2).strip()
        
        if filename and content:
            files[filename] = content
            
    return files

def create_zip_from_files(files: Dict[str, str]) -> bytes:
    """
    Toma un diccionario de archivos y genera un archivo ZIP en memoria (bytes).
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename, content in files.items():
            # Escribir el contenido del archivo en el ZIP
            zipf.writestr(filename, content.encode('utf-8'))
            
    # Mover el puntero del buffer al inicio y retornar los bytes
    buffer.seek(0)
    return buffer.read()
# ... (fin de las funciones anteriores) ...


def zip_a_texto(zip_bytes: bytes) -> str:
    """
    Toma los bytes de un archivo ZIP, extrae el contenido de todos los archivos
    en memoria y los convierte en un único string estructurado para Gemini.
    """
    bloques = []
    
    # Crear un buffer de bytes para manipular el ZIP en memoria
    buffer = io.BytesIO(zip_bytes)
    
    try:
        with zipfile.ZipFile(buffer, 'r') as zipf:
            
            # Recorrer todos los nombres de archivo dentro del ZIP
            for file_info in zipf.infolist():
                if not file_info.is_dir(): # Ignorar carpetas
                    
                    filename = file_info.filename
                    
                    # Leer el contenido del archivo en memoria
                    with zipf.open(filename) as file:
                        # Intentamos decodificar como UTF-8; si falla, lo ignoramos.
                        try:
                            contenido = file.read().decode("utf-8")
                        except UnicodeDecodeError:
                            print(f"Advertencia: Archivo {filename} no es UTF-8 o es binario. Omitiendo.")
                            continue

                    # Tu formato de salida deseado:
                    bloque = f"--- archivo: {filename} ---\n{contenido}\n--- fin archivo ---"
                    bloques.append(bloque)
                    
    except zipfile.BadZipFile:
        # Manejar caso de archivo no válido
        raise ValueError("El archivo subido no es un ZIP válido.")
        
    return "\n\n".join(bloques)