# Flujo Automatizado de Extracción de Datos (OSINT)

## 🎯 Objetivo
Automatizar la ingesta, procesamiento y estructuración de datos provenientes de múltiples fuentes (**URLs, Imágenes, Texto plano y PDFs**) mediante Inteligencia Artificial local, almacenando la información resultante en una base de datos centralizada.

## 🏗️ Arquitectura del Sistema
El proyecto se ejecuta íntegramente en un entorno local utilizando **Docker Desktop** y aprovecha la aceleración por hardware de **NVIDIA** para el procesamiento de lenguaje natural y visión artificial.

* **Orquestador:** [n8n](https://n8n.io/) (Self-hosted).
* **Motor de IA:** [Ollama](https://ollama.com/) (Modelos: `Llava`, `Qwen2.5-VL` y `Moondream`).
* **Base de Datos:** PostgreSQL / SQLite (Configurable en n8n).
* **Infraestructura:** Docker Compose con soporte para NVIDIA Container Toolkit.

## 🚀 Requisitos Previos
* **SO:** Windows 10/11 con WSL2.
* **Hardware:** GPU NVIDIA (Recomendado: RTX 2060 6GB o superior).
* **Drivers:** NVIDIA Game Ready Drivers + Docker Desktop.

## 🛠️ Instalación y Despliegue

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/osint-automation-flow.git
    cd osint-automation-flow
    ```

2.  **Levantar la infraestructura:**
    ```bash
    docker-compose up -d
    ```

3.  **Descargar modelos de IA necesarios:**
    ```bash
    # Para análisis de documentos (OCR avanzado)
    docker exec -it ollama ollama pull qwen2.5vl:3b
    ```

## 📂 Formatos Soportados
| Formato | Método de Extracción | Herramienta |
| :--- | :--- | :--- |
| **URL** | Scraping de contenido / HTML Parsing | n8n HTTP Request |
| **PDF** | Extracción de texto y visión de tablas | Ollama (Llava/Qwen2.5-VL) |
| **Imágenes** | Análisis visual y OCR | Ollama (Moondream/Llava) |
| **TXT** | Procesamiento de lenguaje natural | Ollama (Llama3 / Mistral) |

## ⚙️ Configuración en n8n
1.  Importar el archivo `workflow.json` (incluido en la carpeta `/workflows`).
2.  Configurar las credenciales de la base de datos.
3.  En el nodo de **Ollama Chat Model**, apuntar a la URL base: `http://ollama:11434`.

## 🗄️ Persistencia de Datos
El proyecto utiliza **Bind Mounts** en Windows para asegurar que la información no se pierda al reiniciar los contenedores:
* `./n8n_data`: Almacena flujos, credenciales y base de datos interna.
* `./ollama_data`: Almacena los modelos descargados (GBs).

## ⚠️ Notas de Rendimiento (RTX 2060)
* Se recomienda el uso de **Qwen2.5-VL (3B)** para procesar recibos y documentos técnicos, ya que mantiene un consumo de VRAM inferior a los 4GB, permitiendo que el sistema sea estable.
* Para flujos masivos de imágenes, utilizar **Moondream** para optimizar el tiempo de respuesta (< 2 segundos por imagen).


CREATE TABLE extracciones_osint (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  primer_nombre text,
  segundo_nombre text,
  primer_apellido text,
  segundo_apellido text,
  tipo_identificacion text,
  numero_identificacion text,
  fecha_nacimiento date,
  departamento text,
  municipio text,
  telefono text,
  correo text
  );
