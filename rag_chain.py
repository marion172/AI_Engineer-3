"""
Capa de Recuperación (Retriever) y Generación Grounded (LCEL) asíncrona.
Implementa el flujo RAG con control estricto de alucinaciones y salida estructurada Pydantic.
"""

import config  # Configuración inicial y compatibilidad de entorno
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

from config import (
    VECTORSTORE_DIR,
    COLLECTION_NAME,
    TOP_K,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
)
from schemas import RAGResponse
from embeddings import get_embedding_function


def get_vectorstore() -> Chroma:
    """
    Carga la base de datos persistente ChromaDB utilizando la misma
    función unificada de embeddings para evitar disparidad de dimensiones.
    """
    if not VECTORSTORE_DIR.exists():
        raise FileNotFoundError(
            f"El almacén vectorial en '{VECTORSTORE_DIR}' no fue encontrado. "
            "Ejecute primero 'python ingest.py' para indexar los documentos."
        )

    embedding_fn = get_embedding_function()
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTORSTORE_DIR),
        embedding_function=embedding_fn,
    )


def get_retriever(k: int = TOP_K):
    """
    Configura y retorna el recuperador semántico (retriever) con un top_k controlado
    (entre 3 y 5) para mitigar el problema del 'Contexto Infinito' y la degradación
    de atención del modelo ('Lost in the Middle').
    """
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


def format_docs(docs: List[Document]) -> str:
    """
    Transformador de documentos: serializa los fragmentos recuperados
    incluyendo su procedencia explícita en los metadatos para trazabilidad.
    """
    if not docs:
        return "NO SE ENCONTRARON FRAGMENTOS RELEVANTES EN LA BASE DE CONOCIMIENTO."

    formatted_chunks = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "Documento no identificado")
        chunk_content = doc.page_content.strip()
        formatted_chunks.append(
            f"--- [FRAGMENTO {idx} | FUENTE: {source}] ---\n{chunk_content}"
        )

    return "\n\n".join(formatted_chunks)


def build_rag_chain():
    """
    Construye la cadena LCEL (LangChain Expression Language) uniendo:
    1. Recuperador (Retriever con top_k)
    2. Transformador de contexto
    3. Prompt de sistema con filtro estricto de veracidad
    4. Modelo de lenguaje (LLM)
    5. PydanticOutputParser tipado con RAGResponse
    """
    retriever = get_retriever(k=TOP_K)

    # Configuración del LLM
    llm_kwargs = {
        "model": OPENAI_MODEL,
        "temperature": 0.0,  # Temperatura cero para máxima determinismo y fidelidad
        "api_key": OPENAI_API_KEY,
    }
    if OPENAI_BASE_URL and "api.openai.com" not in OPENAI_BASE_URL:
        llm_kwargs["base_url"] = OPENAI_BASE_URL

    llm = ChatOpenAI(**llm_kwargs)

    # Parser Pydantic
    parser = PydanticOutputParser(pydantic_object=RAGResponse)
    format_instructions = parser.get_format_instructions()

    # Prompt con filtro de veracidad
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres un asistente técnico especializado de alta precisión y veracidad para la plataforma NovaCore Cloud.\n"
                "Tu única misión es responder a la consulta del usuario basándote EXCLUSIVAMENTE en el CONTEXTO proporcionado.\n\n"
                "REGLAS INVIOLABLES DE VERACIDAD (FILTRO ANTI-ALUCINACIÓN):\n"
                "1. Responde solo con información presente de forma explícita en el CONTEXTO.\n"
                "2. Si la respuesta a la pregunta NO está descrita en el CONTEXTO, no intentes adivinar ni recurras a conocimientos externos. "
                "En su lugar, responde de manera concisa: 'No lo sé' o 'No dispongo de información suficiente en el contexto proporcionado para responder esta consulta'.\n"
                "3. En el campo 'sources', lista los nombres de archivo de los documentos donde hallaste la respuesta exacta. Si no sabes la respuesta o no está en el contexto, deja 'sources' como una lista vacía [].\n"
                "4. En el campo 'confidence', indica 'HIGH' si la información está completamente respaldada por el contexto, o 'INSUFFICIENT_CONTEXT' si la respuesta no se encuentra en el material provisto.\n\n"
                "FORMATO OBLIGATORIO DE SALIDA:\n"
                "{format_instructions}",
            ),
            (
                "human",
                "CONTEXTO DOCUMENTAL:\n"
                "==================================================\n"
                "{context}\n"
                "==================================================\n\n"
                "PREGUNTA DEL USUARIO:\n"
                "{question}\n\n"
                "RESPUESTA FORMATEADA:",
            ),
        ]
    )

    # Cadena LCEL
    chain = (
        RunnableParallel(
            {
                "context": (lambda x: x["question"]) | retriever | format_docs,
                "question": lambda x: x["question"],
                "format_instructions": lambda _: format_instructions,
            }
        )
        | prompt_template
        | llm
        | parser
    )

    return chain


async def get_rag_response(query: str) -> RAGResponse:
    """
    Función asíncrona End-to-End solicitada en el entregable:
    a. Realiza la búsqueda de similitud en ChromaDB.
    b. Construye el prompt incluyendo los fragmentos recuperados.
    c. Llama al LLM de forma asíncrona (ainvoke).
    d. Parsea la respuesta a un modelo Pydantic estructurado.
    """
    chain = build_rag_chain()
    # Ejecución asíncrona de la cadena LCEL
    result: RAGResponse = await chain.ainvoke({"question": query})
    return result

