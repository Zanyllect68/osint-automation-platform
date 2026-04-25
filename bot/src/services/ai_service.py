import logging
import os
import httpx
import ollama
import base64

logger = logging.getLogger(__name__)


async def process_pdf(file_path: str, pdf_service_url: str = "") -> str:
    """Procesa PDF - intenta con servicio, luego LLM para extraer info"""
    try:
        if pdf_service_url and pdf_service_url != "http://localhost:3000":
            async with httpx.AsyncClient() as client:
                with open(file_path, "rb") as f:
                    files = {"file": (file_path, f, "application/pdf")}
                    response = await client.post(
                        f"{pdf_service_url}/extract",
                        files=files,
                        timeout=60.0
                    )
                if response.status_code == 200:
                    return response.text[:4000]
        
        text = extract_pdf_text(file_path)
        
        if not text or len(text) < 50:
            return "PDF vacio o no texto. Envia imagenes del PDF para analizar."
        
        extracted = await extract_info_with_llm(text)
        return extracted
        
    except FileNotFoundError:
        return "Error: Archivo no encontrado"
    except Exception as e:
        logger.error(f"Error process_pdf: {e}")
        return f"Error: {str(e)[:200]}"


def extract_pdf_text(file_path: str) -> str:
    """Extrae texto del PDF"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return ""


async def extract_info_with_llm(text: str) -> str:
    """Usa LLM para extraer info estructurada del texto"""
    prompt = f"""Analiza el siguiente texto y extrae la informacion importante:

Texto:
{text[:3000]}

Extrae en este formato:
- NOMBRES: (lista de nombres propios)
- DOCUMENTOS: (numeros de documento, CC, NIT, etc.)
- TELEFONOS: (numeros telefonicos)
- EMAILS: (correos electronicos)
- DIRECCIONES: (direcciones)
- FECHAS: (fechas importantes)
- OTROS: (cualquier otra info relevante)

Responde solo con la informacion extraida, sin texto extra."""

    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return text[:3000]


async def analyze_pdf_with_vision(file_path: str, model: str) -> str:
    """Analiza PDF como imagenes usando Vision LLM"""
    try:
        pages = convert_pdf_to_images(file_path)
        
        results = []
        for i, img in enumerate(pages[:3]):
            img_b64 = base64.b64encode(img).decode()
            
            response = ollama.chat(
                model=model,
                messages=[{
                    "role": "user",
                    "content": "Extrae toda la informacion de esta pagina: nombres, documentos, telefonos, emails, direcciones, fechas. Responde en formato limpio.",
                    "images": [img_b64]
                }]
            )
            results.append(f"Pag {i+1}:\n{response['message']['content']}")
        
        return "\n\n".join(results)
    except Exception as e:
        return f"Error: {str(e)}"


def convert_pdf_to_images(pdf_path: str):
    """Convierte PDF a lista de imagenes"""
    try:
        from pdf2image import convert_from_path
        return convert_from_path(pdf_path)
    except:
        return []


async def process_image(file_path: str, model: str) -> str:
    """Procesa imagen usando Ollama Vision"""
    try:
        with open(file_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        response = ollama.chat(
            model="llava",
            messages=[{
                "role": "user",
                "content": "Describe esta imagen. Si hay texto o documentos, extrae: nombres, documentos (CC, NIT, etc.), telefonos, emails, direcciones, fechas. Responde en formato limpio.",
                "images": [image_data]
            }]
        )
        return response["message"]["content"][:4000]
    except Exception as e:
        logger.error(f"Error process_image: {e}")
        return f"Error: {str(e)[:200]}"


async def ask_ollama(prompt: str, model: str) -> str:
    """Envía prompt a Ollama"""
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        logger.error(f"Error ask_ollama: {e}")
        return f"Error: {str(e)}"