"""
Script de Ingesta y Vectorización (Setup) para la base de conocimiento local.
Carga documentos desde /data, fragmenta con RecursiveCharacterTextSplitter y
persiste los embeddings en una colección local de ChromaDB.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List

# Asegurar encoding UTF-8 en consola de Windows para evitar errores con caracteres especiales
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import chromadb

from config import (
    DATA_DIR,
    VECTORSTORE_DIR,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from embeddings import get_embedding_function


def load_documents_from_directory(data_path: Path) -> List[Document]:
    """
    Lee todos los archivos .txt y .md en el directorio especificado con codificación UTF-8
    y genera objetos Document de LangChain con metadatos asociados.
    """
    documents = []
    if not data_path.exists():
        raise FileNotFoundError(f"El directorio de datos '{data_path}' no existe.")

    supported_extensions = ["*.md", "*.txt"]
    file_paths = []
    for ext in supported_extensions:
        file_paths.extend(data_path.glob(ext))

    if not file_paths:
        raise ValueError(f"No se encontraron archivos .md o .txt en {data_path}")

    print(f"\n📂 Encontrados {len(file_paths)} archivos para procesar en {data_path}:")
    for file_path in sorted(file_paths):
        print(f"   • {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        doc = Document(
            page_content=content,
            metadata={
                "source": file_path.name,
                "file_path": str(file_path),
            },
        )
        documents.append(doc)

    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Aplica chunking estratégico usando RecursiveCharacterTextSplitter con tiktoken (cl100k_base),
    garantizando que los fragmentos respeten los límites de tokens especificados.
    """
    try:
        # Tokenizador oficial de OpenAI (cl100k_base para embeddings y modelos modernos)
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )
    except Exception:
        # Fallback basado en longitud de caracteres (~4 caracteres por token)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE * 4,
            chunk_overlap=CHUNK_OVERLAP * 4,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )
    
    chunks = text_splitter.split_documents(documents)
    print(f"\n✂️  Estrategia de Chunking:")
    print(f"   • Tamaño por chunk: {CHUNK_SIZE} tokens")
    print(f"   • Overlap: {CHUNK_OVERLAP} tokens")
    print(f"   • Fragmentos totales generados: {len(chunks)}")
    return chunks


def is_database_populated(persist_dir: Path, collection_name: str) -> bool:
    """
    Verifica si la base de datos ChromaDB ya existe y contiene documentos indexados,
    evitando costos innecesarios y llamadas redundantes a la API de embeddings.
    """
    if not persist_dir.exists():
        return False
    try:
        client = chromadb.PersistentClient(path=str(persist_dir))
        collections = client.list_collections()
        for col in collections:
            if col.name == collection_name and col.count() > 0:
                return True
        return False
    except Exception:
        return False


def ingest_data(force_reload: bool = False) -> Chroma:
    """
    Función principal de ingesta:
    1. Verifica si la base de datos ya está poblada.
    2. Si no está poblada (o si force_reload=True), carga los archivos,
       fragmenta el texto y crea la colección en ChromaDB persistente.
    """
    embedding_fn = get_embedding_function()

    already_populated = is_database_populated(VECTORSTORE_DIR, COLLECTION_NAME)

    if already_populated and not force_reload:
        print(f"\n✅ La base de datos vectorial en '{VECTORSTORE_DIR}' ya existe y está poblada.")
        print("   (Usa el flag '--force' para forzar una nueva indexación completa).")
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=str(VECTORSTORE_DIR),
            embedding_function=embedding_fn,
        )
        return vectorstore

    if force_reload and already_populated:
        print(f"\n🔄 Modo '--force' detectado: Limpiando colección previa '{COLLECTION_NAME}'...")
        client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    # 1. Cargar documentos
    raw_docs = load_documents_from_directory(DATA_DIR)

    # 2. Fragmentar documentos
    chunks = split_documents(raw_docs)

    # 3. Guardar y persistir en ChromaDB
    print(f"\n💾 Generando embeddings e indexando en ChromaDB ({VECTORSTORE_DIR})...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_fn,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTORSTORE_DIR),
    )
    print("✅ Ingesta finalizada exitosamente. Colección persistida.")
    return vectorstore


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de Ingesta para ChromaDB")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Fuerza la re-indexación eliminando la base previa",
    )
    args = parser.parse_args()

    ingest_data(force_reload=args.force)

