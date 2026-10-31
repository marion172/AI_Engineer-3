"""
Módulo de embeddings centralizado para garantizar coherencia semántica.
Evita el error #1 de sistemas RAG: disparidad entre el modelo de indexación y consulta.
"""

import os
from langchain_openai import OpenAIEmbeddings
from config import OPENAI_API_KEY, OPENAI_BASE_URL, EMBEDDING_MODEL


def get_embedding_function() -> OpenAIEmbeddings:
    """
    Retorna la instancia unificada de la función de embeddings para todo el sistema RAG.
    
    Asegura que tanto la fase de ingesta (indexación) como la fase de recuperación
    (retrieval) empleen exactamente el mismo espacio vectorial y parámetros.
    """
    if not OPENAI_API_KEY:
        raise ValueError(
            "ERROR: La variable de entorno OPENAI_API_KEY no está configurada. "
            "Por favor, configure su clave en el archivo .env antes de continuar."
        )

    # Si se utiliza una URL personalizada (ej. proxy, OpenRouter u otro compatible)
    kwargs = {
        "model": EMBEDDING_MODEL,
        "api_key": OPENAI_API_KEY,
    }
    
    # Agregar base_url si difiere del estándar de OpenAI
    if OPENAI_BASE_URL and "api.openai.com" not in OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL

    return OpenAIEmbeddings(**kwargs)

