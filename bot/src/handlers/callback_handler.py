import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja callbacks de botones inline"""
    query = update.callback_query
    await query.answer()
    
    text = query.data
    responses = {
        "menu_pdf": "Envia el archivo PDF para procesar",
        "menu_imagen": "Envia una imagen para analizar",
        "menu_persona": "Usa: persona Juan | Garcia | CC | 12345678",
        "menu_buscar": "Usa: buscar Juan"
    }
    await query.message.reply_text(responses.get(text, "Opcion no reconocida"))