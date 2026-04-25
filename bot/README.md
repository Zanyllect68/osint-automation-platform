# Bot OSINT Telegram

Bot de Telegram para recopilacion y busqueda de informacion publica usando IA.

## Caracteristicas

- **PDF**: Extrae texto y usa LLM para analizar
- **Imagenes**: Analiza con Vision LLM (llava)
- **Personas**: Guarda en BD SQLite (evita duplicados)
- **Scraping**: Busca en Google y redes sociales
- **Busqueda**: consulta en Base de Datos

## Requisitos Locales

```bash
pip install -r requirements.txt
```

## Configuracion

Crear archivo `.env`:

```env
TELEGRAM_BOT_TOKEN=tu_token
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:latest
```

## Uso Docker

```bash
# Iniciar todo
docker-compose up -d

# Ver logs
docker-compose logs -f bot
```

## Uso Local

```bash
python src/bot.py
```

## Comandos

| Comando | Descripcion |
|---------|------------|
| `/start` | Menu principal |
| `PDF` | Enviar archivo PDF |
| `IMAGEN` | Enviar imagen |
| `persona Juan\|Garcia\|CC\|12345678\|M\|30` | Guardar persona |
| `buscar Juan` | Buscar en BD |
| `lista` | Listar personas |
| `scrape Juan` | Buscar en web |

## Formato Persona

```
persona PRIMER_NOMBRE | PRIMER_APELLIDO | TIPO_DOC | NUMERO_DOC | SEXO | EDAD

Ejemplo:
persona Juan | Garcia | CC | 12345678 | M | 30
```

## Base de Datos

- `bot/data/osint.db` (SQLite)
- Tablas: personas, documentos, imagenes, textos, urls

## Modelos Ollama

Requiere:
- `llama3:latest` (texto)
- `llava` (vision)

```bash
ollama pull llama3:latest
ollama pull llava
```

## Estructura

```
bot/
├── src/
│   ├── bot.py
│   ├── config.py
│   ├── handlers/
│   │   ├── message_handler.py
│   │   └── callback_handler.py
│   └── services/
│       ├── ai_service.py
│       ├── database.py
│       └── scraper.py
├── .env
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```