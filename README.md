# BaseDeDatosGris - Plataforma de OSINT y Análisis de Datos

## 📋 Descripción General

**BaseDeDatosGris** es una plataforma de **OSINT (Open Source Intelligence)** que recolecta, procesa, limpia y analiza información de fuentes públicas. Integra tres servicios principales para automatizar todo el pipeline de inteligencia:

1. **PDF Service**: Conversión de documentos recolectados (PDFs) a imágenes para OCR y análisis
2. **Ollama**: Motor de IA local para análisis de datos, clasificación y extracción de información
3. **n8n**: Orquestación automatizada de flujos de OSINT (recolección → procesamiento → análisis → limpieza)

---

## 🏗️ Arquitectura del Proyecto - Pipeline de OSINT

```
┌─────────────────────────────────────────────────────────────────────┐
│              N8N - Orquestación de OSINT                            │
│        (Recolección → Procesamiento → Análisis → Limpieza)         │
│                       Puerto: 5678 (HTTPS)                         │
└─────────────────────────────────────────────────────────────────────┘
                    ▲                           ▲
                    │                           │
         ┌──────────┴──────────┐      ┌─────────┴──────────┐
         │                     │      │                    │
┌────────▼─────────────┐  ┌────▼──────────────────────┐   │
│  PDF Service         │  │  Ollama                   │   │
│  (OCR/Procesamiento) │  │  (Análisis con IA)        │   │
│  - Conversión        │  │  - Clasificación          │   │
│  - Extracción        │  │  - Extracción NER         │   │
│  - Normalización     │  │  - Sentimiento            │   │
│  Puerto: 3000        │  │  Puerto: 11434            │   │
└────────┬─────────────┘  └────┬──────────────────────┘   │
         │                     │                          │
         └─────────────────────┴──────────────────────────┘
          Fuentes Públicas → Almacenamiento de Datos
          (APIs, Web, Archivos) → (Base de Datos Gris)
```

---

## 🔧 Componentes Principales

### 1. **PDF Service** (Puerto: 3000)
**Propósito**: Procesar documentos PDF recolectados para extracción y análisis de información.

**Tecnología**: Python + Flask

**Funcionalidad en OSINT**:
- Recibe PDFs descargados de fuentes públicas mediante POST en `/convert`
- Convierte páginas a imágenes PNG de 300 DPI para OCR (Reconocimiento Óptico de Caracteres)
- Permite extracción de texto de documentos digitalizados, reportes, registros públicos
- Comprime todas las imágenes en ZIP para procesamiento batch
- Normaliza y prepara datos para análisis posterior

**Endpoint**:
```
POST /convert
Content-Type: application/octet-stream
Body: [archivo PDF binario de fuente pública]
Response: application/zip [imágenes PNG para OCR/análisis]
```

**Casos de uso OSINT**:
- Digitalización de documentos gubernamentales públicos
- Extracción de reportes de organismos reguladores
- Procesamiento de archivos escaneados desde bases de datos públicas
- Normalización de documentación para análisis posterior

**Dependencias**:
- `pdftoppm`: Conversión de PDFs a imágenes de alta resolución
- Flask: Framework web

---

### 2. **Ollama** (Puerto: 11434)
**Propósito**: Análisis y procesamiento de información recolectada mediante modelos de IA locales.

**Tecnología**: Ollama (Motor de modelos de IA)

**Funcionalidad en OSINT**:
- Ejecuta modelos de lenguaje especializados en análisis de datos públicos
- Clasificación automática de información recolectada
- Extracción de entidades (Named Entity Recognition - NER):
  - Personas
  - Organizaciones
  - Ubicaciones
  - Correos electrónicos
  - Números de teléfono
  - Credenciales expuestas
- Análisis de sentimiento en redes sociales y comunicaciones públicas
- Detección de anomalías y patrones sospechosos
- Análisis de vínculos entre entidades (link analysis)
- Procesamiento de imágenes convertidas por PDF Service (OCR)

**Modelos disponibles**: Los encontrados en `data/ollama_data/models/blobs/` (aprox. 6 modelos especializados)

**Características**:
- Ejecución 100% local (sin enviar datos a servidores externos)
- API REST accesible en `http://ollama:11434`
- Procesamiento rápido para grandes volúmenes de datos

---

### 3. **n8n** (Puerto: 5678)
**Propósito**: Orquestar el pipeline completo de OSINT: recolección → procesamiento → limpieza → análisis.

**Tecnología**: Node.js + n8n

**Funcionalidad en OSINT**:
Coordina flujos de trabajo que automaticen:

1. **Recolección de Datos**:
   - Descarga desde URLs públicas
   - Scraping de sitios web públicos
   - APIs de fuentes públicas (datos gubernamentales, redes sociales, etc.)
   - Webhooks para recibir datos de terceros

2. **Procesamiento**:
   - Envío a PDF Service para conversión y OCR
   - Parsing y normalización de datos
   - Validación de formato

3. **Análisis con IA**:
   - Envío a Ollama para clasificación
   - Extracción de entidades
   - Análisis de relaciones
   - Generación de reportes

4. **Limpieza de Datos**:
   - Deduplicación
   - Validación de integridad
   - Eliminación de datos sensibles innecesarios
   - Normalización de formatos

5. **Almacenamiento**:
   - Guardado en bases de datos
   - Exportación en múltiples formatos
   - Archivo de histórico

**Interfaz**:
- Editor visual para crear flujos sin código
- Integración nativa con PDF Service y Ollama
- Soporte para webhooks bidireccionales
- Programación de tareas automáticas
- Almacenamiento de flujos en `data/n8n/storage/workflows/`

**Variables de entorno configuradas**:
- `N8N_HOST`: 0.0.0.0 (accesible desde cualquier interfaz)
- `N8N_PORT`: 5678
- `N8N_PROTOCOL`: HTTPS (seguridad)
- `OLLAMA_HOST`: http://ollama:11434 (conexión interna para análisis)
- `WEBHOOK_URL`: https://sticks-bbs-might-postcards.trycloudflare.com/ (para webhooks externos)
- `N8N_RUNNERS_ENABLED`: true (ejecución paralela de múltiples trabajos de OSINT)

---

## 📊 Flujo de Trabajo OSINT Típico

```
1. RECOLECCIÓN DE DATOS
   └─► Fuentes públicas (APIs, web scraping, archivos, webhooks)
        ↓
2. DESCARGA Y ALMACENAMIENTO TEMPORAL
   └─► n8n recibe datos de fuentes públicas
        ↓
3. PROCESAMIENTO DE DOCUMENTOS
   └─► PDF Service convierte documentos a imágenes
        └─► OCR y normalización
        ↓
4. ANÁLISIS CON IA
   └─► Ollama analiza los datos:
        ├─► Clasificación automática
        ├─► Extracción de entidades (NER)
        ├─► Análisis de sentimiento
        └─► Detección de patrones
        ↓
5. LIMPIEZA DE DATOS
   └─► Deduplicación
       └─► Validación
       └─► Normalización
        ↓
6. ENRIQUECIMIENTO
   └─► Vinculación de entidades (link analysis)
       └─► Geolocalización
       └─► Análisis temporal
        ↓
7. ALMACENAMIENTO EN BASE DE DATOS GRIS
   └─► Datos procesados y limpios
       └─► Histórico de actualizaciones
       └─► Índices para búsqueda
        ↓
8. GENERACIÓN DE REPORTES
   └─► Inteligencia procesada lista para análisis
```

---

## 🚀 Requisitos y Configuración

### Requisitos del Sistema
- Docker y Docker Compose
- Mínimo 4GB de RAM (recomendados 8GB para Ollama)
- Espacio en disco: ~10GB (modelos de IA)

### Variables de Entorno Críticas
```
OLLAMA_HOST=http://ollama:11434    # Conexión interna
WEBHOOK_URL=<tu-dominio-público>   # Para webhooks remotos
N8N_PROTOCOL=https                 # Seguridad
```

---

## 📂 Estructura de Directorios

```
BaseDeDatosGris/
├── docker-compose.yml           # Orquestación de contenedores
├── README.md                    # Este archivo
├── data/
│   ├── n8n/                     # Datos persistentes de n8n
│   │   ├── config/              # Configuración
│   │   ├── storage/
│   │   │   └── workflows/       # Flujos guardados
│   │   └── nodes/               # Nodos personalizados
│   └── ollama_data/             # Datos persistentes de Ollama
│       └── models/              # Modelos de IA descargados
├── doc/
│   └── arquitectura.md          # Documentación técnica
├── infra/
│   └── scripts/                 # Scripts de infraestructura
└── service/
    ├── n8n/
    │   ├── Dockerfile           # Configuración de imagen
    │   ├── README.txt
    │   └── template.json        # Plantilla de flujos
    ├── ollama/                  # Configuración de Ollama
    └── pdf-service/
        ├── Dockerfile           # Contenedor Python
        └── server.py            # Servidor Flask
```

---

## 🔗 Conectividad Entre Servicios

| De | A | URL Interna | Puerto |
|---|---|---|---|
| n8n | PDF Service | http://pdf:3000 | 3000 |
| n8n | Ollama | http://ollama:11434 | 11434 |
| PDF Service | - | - | - |
| Ollama | - | - | - |

---

## 🛠️ Personalización para OSINT

### Configurar nuevas fuentes de datos públicas
- En n8n: crear nodos HTTP GET, webhooks o conectores de APIs publicas
- Ejemplos: APIs REST de datos abiertos, endpoints de búsqueda, feeds RSS
- Guardar flujos en: `service/n8n/workflows/`

### Especializar modelos de análisis en Ollama
- Editar y entrenar modelos para dominios específicos:
  - Análisis de redes sociales
  - Detección de desinformación
  - Análisis de documentos técnicos
  - Identificación de conexiones entre entidades
- Modelos guardados en: `data/ollama_data/models/`

### Personalizar procesamiento de documentos
- Editar: `service/pdf-service/server.py`
- Parámetros ajustables:
  - Resolución DPI (actualmente 300)
  - Formatos de salida
  - Preprocesamiento para OCR
  - Extracción de metadatos de PDFs

### Agregar filtros de limpieza de datos
- En n8n: crear nodos de transformación personalizada
- Implementar reglas de:
  - Validación de formatos
  - Detección de duplicados
  - Anonimización de datos sensibles
  - Validación de integridad

### Integrar con bases de datos OSINT
- Conectores disponibles en n8n:
  - PostgreSQL/MySQL
  - MongoDB
  - Elasticsearch
  - Apache Solr
- Guardar histórico y hacer búsquedas avanzadas

---

## 🐳 Inicio Rápido

```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

---

## 📡 Acceso a los Servicios

| Servicio | URL | Propósito |
|---|---|---|
| n8n | https://localhost:5678 | Dashboard de orquestación de flujos OSINT |
| PDF Service | http://localhost:3000/convert | Endpoint para procesar documentos (POST) |
| Ollama API | http://localhost:11434/api/generate | API para análisis con IA |

### Ejemplos de Uso:

**Enviar PDF para procesamiento:**
```bash
curl -X POST http://localhost:3000/convert \
  --data-binary @documento_publico.pdf \
  -o documentos_procesados.zip
```

**Consultar a Ollama para análisis:**
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "neural-chat",
    "prompt": "Analiza esta información pública y extrae entidades principal",
    "stream": false
  }'
```

**Crear flujo OSINT en n8n:**
- Acceder a https://localhost:5678
- Crear nuevo workflow
- Conectar nodos: HTTP → PDF Service → Ollama → Database
- Programar ejecución automática

---

## 🔒 Seguridad y Consideraciones Éticas para OSINT

### Seguridad Técnica:
1. **HTTPS en n8n**: Activo solo si está detrás de proxy (certificados válidos)
2. **API Ollama**: No requiere autenticación (asegurar acceso restringido a red local)
3. **Persistencia**: Base de datos en `data/` - hacer backups regulares
4. **Aislamiento**: Uso de Docker para segregar servicios
5. **Logs**: Auditar accesos y cambios en datos

### Consideraciones Legales y Éticas:
1. **Cumplimiento Legal**:
   - Respetar términos de servicio de cada fuente
   - Verificar legalidad del scraping en la jurisdicción
   - Cumplir con GDPR, CCPA y leyes de privacidad locales
   - Revisar políticas de robots.txt

2. **Ética de OSINT**:
   - Solo recolectar datos públicamente accesibles
   - No realizar fuerza bruta ni ataques
   - Proteger privacidad de individuos
   - No difundir información personal sin consentimiento
   - Mantener trazabilidad de fuentes

3. **Responsabilidad**:
   - Documentar todas las fuentes utilizadas
   - Mantener histórico de cambios
   - Realizar auditorías regularmente
   - Cumplir con políticas organizacionales

### Datos Sensibles:
- Implementar anonimización automática
- Clasificar datos por nivel de sensibilidad
- Aplicar reglas de retención
- Cifrado en reposo si es necesario

---

## 📝 Notas Importantes para OSINT

- **Fuentes Públicas**: Asegurar que todos los datos recolectados provengan de fuentes públicamente accesibles
- **Cumplimiento Legal**: Respetar términos de servicio de cada fuente (robots.txt, CFAA, GDPR, etc.)
- **Privacidad**: Los datos procesados quedan almacenados localmente (sin envío a servidores externos)
- **Anonimización**: Implementar reglas para proteger datos personales innecesarios
- **Primeros inicios**: Ollama tarda en descargar modelos (ver logs con `docker-compose logs ollama`)
- **Almacenamiento**: Datos temporales en `/tmp` se limpian automáticamente
- **Rendimiento**: Los modelos de IA se ejecutan localmente; escalar n8n runners si hay muchos trabajos
- **Base de datos**: SQLite en `data/n8n/database.sqlite` con WAL habilitado para mejor concurrencia
- **Histórico**: Mantener copias de respaldo de `data/` para auditoría y trazabilidad
- **Actualizaciones**: Monitorizar fuentes públicas regularmente con `scheduled workflows` en n8n

---

## 🌐 Fuentes de Datos OSINT Soportadas

n8n puede conectarse con múltiples fuentes públicas:

### APIs de Datos Abiertos:
- Datos gubernamentales (Open Data portals)
- APIs públicas de redes sociales (Twitter, LinkedIn, etc.)
- Registros de dominios (WHOIS)
- Bases de datos de vulnerabilidades (CVE, Shodan)
- APIs meteorológicas y geográficas

### Web Scraping:
- HypothesisHTML Parser para extracción de contenido
- Manejo de JavaScript dinámico
- Respetar robots.txt y términos de servicio

### Bases de Datos Públicas:
- PostgreSQL/MySQL con datos públicos
- Elasticsearch para búsquedas masivas
- APIs de búsqueda de documentos

### Comunicaciones:
- Webhooks para recibir datos de terceros
- SMTP para notificaciones de nuevos datos
- Integración con sistemas de tickets

### Almacenamiento y Exportación:
- Bases de datos locales
- S3, Drive, etc. para archivos
- Formatos: JSON, CSV, Excel, HTML
- APIs para publicar inteligencia procesada

---

## 📞 Soporte y Documentación

- [n8n Docs](https://docs.n8n.io/)
- [Ollama Docs](https://ollama.ai/)
- [Flask Docs](https://flask.palletsprojects.com/)
- [Poppler Docs](https://poppler.freedesktop.org/)

---

**Última actualización**: Abril 2026
**Tipo de proyecto**: Plataforma de OSINT (Open Source Intelligence)
**Estado**: En desarrollo y producción
**Versión**: 1.0
