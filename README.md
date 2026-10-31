# Sistema de Recuperación Semántica Local (RAG)

Sistema de Recuperación Semántica Local (RAG - Retrieval-Augmented Generation) implementado de extremo a extremo (End-to-End) con Python, LangChain (LCEL), ChromaDB y Pydantic.

El sistema recibe consultas del usuario, busca los fragmentos más relevantes en una base de datos vectorial local previamente indexada y genera respuestas fundamentadas estrictamente en dicho contexto, garantizando la mitigación activa de alucinaciones.

---

## Arquitectura del Sistema

```
                          [ Documentos en /data ]
                                     │
                                     ▼
                     [ RecursiveCharacterTextSplitter ]
                        (500 tokens / 50 overlap)
                                     │
                                     ▼
                           [ OpenAIEmbeddings ]
                                     │
                                     ▼
                      [ ChromaDB Local (./vectorstore) ]
                                     │
  [ Consulta del Usuario ] ──────────┼─────────────────────┐
                                     │                     │
                                     ▼                     ▼
                           [ Retriever (top_k=4) ]  [ Prompt Template ]
                                     │             (Filtro de Veracidad)
                                     └───────────►         │
                                                           ▼
                                                   [ LLM Asíncrono ]
                                                           │
                                                           ▼
                                                [ PydanticOutputParser ]
                                                           │
                                                           ▼
                                                  [ RAGResponse JSON ]
```

---

## Estructura del Repositorio

```text
AI_Engineer-3/
├── data/                               # Dataset documental de ejemplo (.md)
│   ├── 01_manual_seguridad_accesos.md  # Políticas de acceso, MFA, RBAC y VPN
│   ├── 02_manual_despliegue_ci_cd.md   # Flujo trunk-based, pruebas y rollback
│   ├── 03_politica_retencion_datos.md  # Clasificación, anonimización y retención
│   └── 04_gestion_incidentes_soporte.md# SLAs de incidentes Sev-1 a Sev-4 y guardias
├── .env.example                        # Plantilla de variables de entorno
├── .gitignore                          # Exclusión de venv, .env y vectorstore
├── requirements.txt                    # Dependencias del proyecto
├── config.py                           # Parámetros y carga centralizada de configuración
├── schemas.py                          # Modelo Pydantic para respuesta tipada (RAGResponse)
├── embeddings.py                       # Módulo unificado de Embeddings (evita disparidad)
├── ingest.py                           # Script de carga, chunking y persistencia en ChromaDB
├── rag_chain.py                        # Cadena LCEL asíncrona y función get_rag_response()
├── main.py                             # Script de ejecución con las 2 pruebas requeridas
├── demo.ipynb                          # Notebook interactivo para ejecución paso a paso
└── README.md                           # Documentación técnica completa
```

---

## Decisiones Técnicas y Prevención de Errores Comunes

| Error Común Señalado | Solución Implementada en este Proyecto |
|---|---|
| El "Contexto Infinito" / Lost in the Middle | El retriever está parametrizado con `top_k = 4` (`search_kwargs={"k": 4}`). Solo se inyectan en el prompt los fragmentos más relevantes, optimizando costos de tokens y concentración de atención del LLM. |
| Embeddings no coincidentes | Se centralizó la instanciación en `embeddings.py` (`get_embedding_function()`). Tanto la ingesta en `ingest.py` como la consulta en `rag_chain.py` consumen exactamente el mismo modelo y parámetros. |
| Falta de persistencia | La función `is_database_populated()` verifica si `./vectorstore` ya cuenta con la colección y documentos indexados. Si ya existe, se reutiliza sin volver a gastar llamadas de API de embeddings. Permite forzar reindexación con `--force`. |
| Alucinaciones en preguntas fuera de contexto | Se diseñó un System Prompt como "filtro de veracidad" con instrucciones explícitas de responder "No lo sé" o "No dispongo de información" y dejar la lista de `sources` vacía cuando la respuesta no esté en el contexto. |
| Salida no estructurada | Integración nativa de `PydanticOutputParser` tipado con el modelo `RAGResponse`, asegurando que cada respuesta contenga campos validados: `answer`, `sources` y `confidence`. |

---

## Instalación y Puesta en Marcha

### 1. Clonar el repositorio y crear el entorno virtual

```bash
# Crear entorno virtual con Python 3.10 o superior
python -m venv .venv

# Activar en Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# O en Linux/macOS:
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia la plantilla `.env.example` como `.env`:

```bash
cp .env.example .env
```

Edita `.env` e introduce tu clave de API:

```env
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIRECTORY=./vectorstore
CHROMA_COLLECTION_NAME=Company_knowledge_base
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=4
```

> **Nota:** También es compatible con endpoints compatibles como OpenRouter especificando `OPENAI_BASE_URL=https://openrouter.ai/api/v1`.

---

## Uso y Ejecución

### Opción A: Ejecución de las Pruebas Automatizadas (Recomendado)

El script `main.py` detecta si la base de datos está indexada (si no lo está, ejecuta la ingesta de forma automática) y corre de manera asíncrona las dos evaluaciones solicitadas:

```bash
python main.py
```

### Opción B: Ingesta Manual de Documentos

Si deseas ejecutar o forzar la vectorización por separado:

```bash
# Ingesta normal (omite si ya está poblada)
python ingest.py

# Forzar re-indexación completa
python ingest.py --force
```

### Opción C: Notebook Interactivo

Puedes abrir y ejecutar celda a celda el notebook interactivo:

```bash
jupyter notebook demo.ipynb
```

---

## Pruebas Realizadas y Resultados

### Prueba 1: Pregunta Válida (Información Presente)
- **Consulta:** *"¿Cuál es el tiempo máximo de primera respuesta (SLA) para un incidente Sev-1 y a quién se debe escalar si la causa raíz no se identifica en los primeros 20 minutos?"*
- **Comportamiento esperado:** Respuesta precisa citando los 15 minutos de SLA y el escalamiento al Engineering Lead y Director de Infraestructura, referenciando `04_gestion_incidentes_soporte.md`.
- **Resultado:**
  ```json
  {
    "answer": "Para un incidente Sev-1 (Crítico), el tiempo máximo de primera respuesta (SLA) es de 15 minutos. Si la causa raíz no es identificada en los primeros 20 minutos, se debe escalar automáticamente al Engineering Lead y al Director de Infraestructura.",
    "sources": [
      "04_gestion_incidentes_soporte.md"
    ],
    "confidence": "HIGH"
  }
  ```

### Prueba 2: Pregunta Trampa (Información Ausente / Anti-Alucinación)
- **Consulta:** *"¿Cuál es el procedimiento para solicitar el reembolso de gastos de almuerzo y cuántos días de vacaciones anuales le corresponden a un desarrollador senior?"*
- **Comportamiento esperado:** El modelo no debe inventar políticas de beneficios ni recursos humanos que no están en la documentación técnica; debe declarar que no lo sabe y devolver fuentes vacías.
- **Resultado:**
  ```json
  {
    "answer": "No dispongo de información suficiente en el contexto proporcionado para responder esta consulta sobre reembolsos de gastos de almuerzo ni días de vacaciones.",
    "sources": [],
    "confidence": "INSUFFICIENT_CONTEXT"
  }
  ```

---

## Seguridad

- Las llaves de API nunca se suben al control de versiones; se gestionan de forma segura a través de `.env` (ignorado en `.gitignore`).
- La base vectorial local se almacena en la carpeta excluida `./vectorstore`.

