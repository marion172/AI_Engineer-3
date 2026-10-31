"""
Módulo de configuración centralizada del sistema RAG.
Carga y valida las variables de entorno desde el archivo .env.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Desactivar telemetría de ChromaDB
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
try:
    import posthog
    posthog.capture = lambda *args, **kwargs: None
except Exception:
    pass

# Evitar dependencias innecesarias de ONNX Runtime en ChromaDB
# dado que este proyecto utiliza OpenAIEmbeddings vía OpenRouter/OpenAI
if "onnxruntime" not in sys.modules:
    try:
        import onnxruntime
    except (ImportError, Exception):
        from unittest.mock import MagicMock
        sys.modules["onnxruntime"] = MagicMock()

# Cargar variables de entorno desde .env si existe
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Configuración de carpetas
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", str(BASE_DIR / "vectorstore")))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "Company_knowledge_base")

# Configuración de chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Configuración de recuperación (Top K)
TOP_K = int(os.getenv("TOP_K", "4"))

# Configuración del LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "nvidia/nemotron-3.5-lightning:free")

# Configuración de Embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

