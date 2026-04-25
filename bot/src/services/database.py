import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "osint.db")


def init_db():
    """Inicializa la base de datos"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            primer_nombre TEXT,
            segundo_nombre TEXT,
            primer_apellido TEXT,
            segundo_apellido TEXT,
            tipo_documento TEXT,
            numero_documento TEXT,
            sexo TEXT,
            edad INTEGER,
            fecha_nacimiento TEXT,
            tipo_sangre TEXT,
            direccion TEXT,
            fuente TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            filename TEXT,
            contenido TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imagenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            filename TEXT,
            descripcion TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            url TEXT,
            contenido TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS textos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            contenido TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_persona(data: dict):
    """Guarda datos de una persona - actualiza si ya existe"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    doc = data.get("numero_documento", "").strip()
    if doc:
        cursor.execute("SELECT id FROM personas WHERE numero_documento = ?", (doc,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE personas SET 
                    primer_nombre = COALESCE(?, primer_nombre),
                    segundo_nombre = COALESCE(?, segundo_nombre),
                    primer_apellido = COALESCE(?, primer_apellido),
                    segundo_apellido = COALESCE(?, segundo_apellido),
                    tipo_documento = COALESCE(?, tipo_documento),
                    sexo = COALESCE(?, sexo),
                    edad = COALESCE(?, edad),
                    fecha_nacimiento = COALESCE(?, fecha_nacimiento),
                    tipo_sangre = COALESCE(?, tipo_sangre),
                    direccion = COALESCE(?, direccion)
                WHERE numero_documento = ?
            """, (
                data.get("primer_nombre", ""),
                data.get("segundo_nombre", ""),
                data.get("primer_apellido", ""),
                data.get("segundo_apellido", ""),
                data.get("tipo_documento", ""),
                data.get("sexo", ""),
                data.get("edad", 0),
                data.get("fecha_nacimiento", ""),
                data.get("tipo_sangre", ""),
                data.get("direccion", ""),
                doc
            ))
            conn.commit()
            conn.close()
            return "actualizado"
    
    cursor.execute("""
        INSERT INTO personas (
            chat_id, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
            tipo_documento, numero_documento, sexo, edad, fecha_nacimiento,
            tipo_sangre, direccion, fuente
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("chat_id"),
        data.get("primer_nombre", ""),
        data.get("segundo_nombre", ""),
        data.get("primer_apellido", ""),
        data.get("segundo_apellido", ""),
        data.get("tipo_documento", ""),
        data.get("numero_documento", ""),
        data.get("sexo", ""),
        data.get("edad", 0),
        data.get("fecha_nacimiento", ""),
        data.get("tipo_sangre", ""),
        data.get("direccion", ""),
        data.get("fuente", "")
    ))
    conn.commit()
    conn.close()
    return "creado"


def get_personas():
    """Lista todas las personas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personas ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_documento(chat_id: int, filename: str, contenido: str):
    """Guarda un documento PDF"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documentos (chat_id, filename, contenido) VALUES (?, ?, ?)",
        (chat_id, filename, contenido)
    )
    conn.commit()
    conn.close()


def save_imagen(chat_id: int, filename: str, descripcion: str):
    """Guarda una imagen"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imagenes (chat_id, filename, descripcion) VALUES (?, ?, ?)",
        (chat_id, filename, descripcion)
    )
    conn.commit()
    conn.close()


def save_url(chat_id: int, url: str, contenido: str = ""):
    """Guarda una URL"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO urls (chat_id, url, contenido) VALUES (?, ?, ?)",
        (chat_id, url, contenido)
    )
    conn.commit()
    conn.close()


def save_texto(chat_id: int, contenido: str):
    """Guarda un texto"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO textos (chat_id, contenido) VALUES (?, ?)",
        (chat_id, contenido)
    )
    conn.commit()
    conn.close()


def buscar(palabra: str) -> list:
    """Busca en todas las tablas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA case_sensitive = 0")
    
    resultados = []
    palabra_like = f"%{palabra}%"
    
    cursor.execute("""
        SELECT id, primer_nombre, primer_apellido, numero_documento, fecha 
        FROM personas 
        WHERE primer_nombre LIKE ? OR segundo_nombre LIKE ? OR primer_apellido LIKE ? OR segundo_apellido LIKE ?
    """, (palabra_like, palabra_like, palabra_like, palabra_like))
    for row in cursor.fetchall():
        resultados.append(f"[PER] {row[1]} {row[2]} - DOC: {row[3]} - {row[4]}")
    
    cursor.execute("SELECT id, filename, contenido, fecha FROM documentos WHERE contenido LIKE ?", (palabra_like,))
    for row in cursor.fetchall():
        resultados.append(f"[PDF] {row[1]} - {row[3]}")
    
    cursor.execute("SELECT id, filename, descripcion, fecha FROM imagenes WHERE descripcion LIKE ?", (palabra_like,))
    for row in cursor.fetchall():
        resultados.append(f"[IMG] {row[1]} - {row[3]}")
    
    cursor.execute("SELECT id, url, contenido, fecha FROM urls WHERE url LIKE ? OR contenido LIKE ?", (palabra_like, palabra_like))
    for row in cursor.fetchall():
        resultados.append(f"[URL] {row[1]} - {row[3]}")
    
    cursor.execute("SELECT id, contenido, fecha FROM textos WHERE contenido LIKE ?", (palabra_like,))
    for row in cursor.fetchall():
        resultados.append(f"[TXT] {row[1][:50]}... - {row[2]}")
    
    conn.close()
    return resultados


def get_all_personas() -> list:
    """Lista todas las personas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, primer_nombre, primer_apellido, tipo_documento, numero_documento, edad FROM personas ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_documentos() -> list:
    """Lista todos los documentos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, fecha FROM documentos ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_imagenes() -> list:
    """Lista todas las imagenes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, descripcion, fecha FROM imagenes ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_estadisticas() -> dict:
    """Obtiene estadisticas de la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM personas")
    personas_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM documentos")
    documentos_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM imagenes")
    imagenes_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM textos")
    textos_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "personas": personas_count,
        "documentos": documentos_count,
        "imagenes": imagenes_count,
        "textos": textos_count
    }


init_db()