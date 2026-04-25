import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.ai_service import process_pdf, process_image
from services.database import save_documento, save_imagen, save_url, save_texto, buscar, save_persona, get_all_personas, get_all_documentos, get_all_imagenes, get_estadisticas
from services.scraper import scrape_google, scrape_person, extract_emails, extract_phones, extract_documents, extract_nombres

logger = logging.getLogger(__name__)

HELLO_MESSAGE = """
Bienvenido al Bot OSINT

Que deseas hacer?

1. PDF - Enviar un documento PDF
2. IMAGEN - Enviar una imagen para analizar
3. PERSONA - Registrar datos de persona
4. BUSCAR - Buscar en la base de datos

Escribe el numero o palabra clave
"""

MENU_KEYBOARD = [
    [InlineKeyboardButton("PDF", callback_data="menu_pdf")],
    [InlineKeyboardButton("IMAGEN", callback_data="menu_imagen")],
    [InlineKeyboardButton("PERSONA", callback_data="menu_persona")],
    [InlineKeyboardButton("BUSCAR", callback_data="menu_buscar")],
]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup(MENU_KEYBOARD)
    await update.message.reply_text(HELLO_MESSAGE, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(
        f"Info del Chat:\nID: {chat.id}\nTipo: {chat.type}"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    chat_id = update.effective_chat.id

    if text in ["salir", "exit"]:
        await update.message.reply_text("Chao! Hasta pronto.")
    
    elif text.startswith("buscar "):
        palabra = text[7:].strip()
        resultados = buscar(palabra)
        if resultados:
            msg = f"Resultados para '{palabra}':\n\n" + "\n".join(resultados[:10])
        else:
            msg = f"No se encontraron resultados para '{palabra}'"
        await update.message.reply_text(msg)
    
    elif text.startswith("scrape ") or text.startswith("scan "):
        query = text.replace("scrape ", "").replace("scan ", "").strip()
        await update.message.reply_text(f"Buscando info de '{query}'...")
        
        resultados = await scrape_person(query)
        msg = f"Resultados para {query}:\n\n"
        
        if resultados.get("google"):
            msg += f"Google: {len(resultados['google'])} resultados\n"
        
        if resultados.get("emails"):
            msg += f"Emails: {', '.join(resultados['emails'][:5])}\n"
        
        if resultados.get("telefonos"):
            msg += f"Telefonos: {', '.join(resultados['telefonos'][:5])}\n"
        
        if resultados.get("documentos"):
            msg += f"Documentos: {', '.join(resultados['documentos'][:5])}\n"
        
        if not resultados.get("google"):
            msg += "No se encontraron resultados"
        
        await update.message.reply_text(msg)
    
    elif text.startswith("persona "):
        data = parse_persona_text(update.message.text, chat_id)
        if data.get("primer_nombre"):
            resultado = save_persona(data)
            await update.message.reply_text(f"{data['primer_nombre']} {data['primer_apellido']} - {resultado.upper()}")
        else:
            await update.message.reply_text("Formato incorrecto. Usa: persona Juan | Garcia | CC | 12345678 | M | 30")
    
    elif text in ["lista", "listar"]:
        msg = "Lista de personas:\n\n"
        personas = get_all_personas()
        for p in personas[:10]:
            msg += f"{p[0]}. {p[1]} {p[2]} - {p[3]}: {p[4]}\n"
        await update.message.reply_text(msg)
    
    elif text in ["docs", "documentos"]:
        msg = "Documentos:\n\n"
        docs = get_all_documentos()
        for d in docs[:10]:
            msg += f"{d[0]}. {d[1]} - {d[2]}\n"
        await update.message.reply_text(msg)
    
    elif text in ["fotos", "imagenes"]:
        msg = "Imagenes:\n\n"
        imgs = get_all_imagenes()
        for i in imgs[:10]:
            msg += f"{i[0]}. {i[1]} - {i[3]}\n"
        await update.message.reply_text(msg)
    
    elif text in [" stats", "estadisticas", "info"]:
        stats = get_estadisticas()
        await update.message.reply_text(
            f"Estadisticas:\n\n"
            f"Personas: {stats['personas']}\n"
            f"Documentos: {stats['documentos']}\n"
            f"Imagenes: {stats['imagenes']}\n"
            f"Textos: {stats['textos']}"
        )
    
    elif text in ["pdf"]:
        await update.message.reply_text("Envia el archivo PDF")
    
    elif text in ["imagen", "img"]:
        await update.message.reply_text("Envia la imagen")
    
    elif text in ["persona", "personas"]:
        await update.message.reply_text(
            "Registrar persona:\n\n"
            "Usa este formato:\n"
            "persona PRIMER_NOMBRE | PRIMER_APELLIDO | TIPO_DOC | NUMERO_DOC | SEXO | EDAD\n\n"
            "Ejemplo:\n"
            "persona Juan | Garcia | CC | 12345678 | M | 30"
        )
    
    elif text in ["buscar"]:
        await update.message.reply_text("Buscar:\n\nEjemplo: buscar Juan")
    
    else:
        save_texto(chat_id, update.message.text)
        await start_command(update, context)


def parse_persona_text(text: str, chat_id: int) -> dict:
    data = {"chat_id": chat_id, "fuente": "texto"}
    
    parts = text[8:].split("|")
    if len(parts) >= 2:
        data["primer_nombre"] = parts[0].strip()
        data["primer_apellido"] = parts[1].strip()
        data["tipo_documento"] = parts[2].strip() if len(parts) > 2 else ""
        data["numero_documento"] = parts[3].strip() if len(parts) > 3 else ""
        data["sexo"] = parts[4].strip() if len(parts) > 4 else ""
        data["edad"] = int(parts[5].strip()) if len(parts) > 5 and parts[5].strip().isdigit() else 0
    
    return data


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    chat_id = update.effective_chat.id

    if document.mime_type == "application/pdf":
        logger.info(f"PDF recibido: {document.file_name}")
        await update.message.reply_text("Procesando PDF...")
        
        file = await document.get_file()
        file_path = f"temp_{document.file_name}"
        await file.download_to_drive(file_path)
        
        from config import Config
        result = await process_pdf(file_path, Config.PDF_SERVICE_URL)
        
        save_documento(chat_id, document.file_name, result)
        
        extracted_data = extract_documents(result)
        extracted_emails_list = extract_emails(result)
        extracted_phones_list = extract_phones(result)
        
        nombres = extract_nombres(result)
        
        msg = f"PDF PROCESSADO!\n"
        msg += f"========================\n\n"
        
        if nombres:
            msg += f"NOMBRES: {nombres[:5]}\n"
        
        if extracted_data:
            msg += f"DOCUMENTOS: {', '.join(extracted_data[:10])}\n"
        
        if extracted_emails_list:
            msg += f"EMAILS: {', '.join(extracted_emails_list[:10])}\n"
        
        if extracted_phones_list:
            msg += f"TELEFONOS: {', '.join(extracted_phones_list[:10])}\n"
        
        msg += f"\n========================\n"
        msg += f"Guardado en BD: {document.file_name}\n"
        msg += f"Chars: {len(result)}"
        
        await update.message.reply_text(msg)
        
        if os.path.exists(file_path):
            os.remove(file_path)
    else:
        await update.message.reply_text("Solo se aceptan archivos PDF")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import Config
    
    chat_id = update.effective_chat.id
    await update.message.reply_text("Analizando imagen...")
    
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = f"temp_photo_{photo.file_id}.jpg"
    await file.download_to_drive(file_path)
    
    result = await process_image(file_path, Config.OLLAMA_MODEL)
    
    save_imagen(chat_id, f"{photo.file_id}.jpg", result)
    
    extracted_data = extract_documents(result)
    emails = extract_emails(result)
    phones = extract_phones(result)
    
    msg = f"IMAGEN ANALIZADA!\n"
    msg += f"======================\n\n"
    
    if extracted_data:
        msg += f"DOCUMENTOS: {', '.join(extracted_data[:10])}\n"
    if emails:
        msg += f"EMAILS: {', '.join(emails[:10])}\n"
    if phones:
        msg += f"TELEFONOS: {', '.join(phones[:10])}\n"
    
    msg += f"\n----------------------\n"
    msg += f"Descripcion: {result[:1500]}\n"
    msg += f"\nGuardado en BD: SI"
    
    await update.message.reply_text(msg)
    
    if os.path.exists(file_path):
        os.remove(file_path)