"""
Punto de entrada principal para ejecutar las pruebas del sistema RAG.
Ejecuta de manera asíncrona dos pruebas clave:
1. Pregunta válida con respuesta respaldada en los documentos.
2. Pregunta trampa cuya respuesta no existe en la base documental (filtro anti-alucinación).
"""

import asyncio
import json
from pathlib import Path
from ingest import ingest_data, is_database_populated
from rag_chain import get_rag_response
from config import VECTORSTORE_DIR, COLLECTION_NAME


def print_separator(title: str = ""):
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


async def run_evaluations():
    print_separator("SISTEMA DE RECUPERACION SEMANTICA LOCAL (RAG) - PRUEBAS")

    # Asegurar que la base de datos esté lista
    if not is_database_populated(VECTORSTORE_DIR, COLLECTION_NAME):
        print("[INFO] Base vectorial no detectada. Iniciando ingesta automatica...")
        ingest_data(force_reload=False)
    else:
        print(f"[OK] Base vectorial detectada en '{VECTORSTORE_DIR}' ({COLLECTION_NAME}).")

    # Definición de las dos pruebas requeridas
    test_cases = [
        {
            "id": "PRUEBA 1: Pregunta Valida (Informacion Presente en el Corpus)",
            "query": (
                "¿Cual es el tiempo maximo de primera respuesta (SLA) para un incidente Sev-1 "
                "y a quien se debe escalar si la causa raiz no se identifica en los primeros 20 minutos?"
            ),
            "expected_behavior": "El modelo debe responder con precision citando el SLA de 15 minutos y escalamiento a Engineering Lead y Director de Infraestructura.",
        },
        {
            "id": "PRUEBA 2: Pregunta Trampa (Informacion Ausente en el Corpus)",
            "query": (
                "¿Cual es el procedimiento para solicitar el reembolso de gastos de almuerzo "
                "y cuantos dias de vacaciones anuales le corresponden a un desarrollador senior?"
            ),
            "expected_behavior": "El modelo NO debe alucinar; debe indicar 'No lo se' o que no posee dicha informacion, con fuentes vacias.",
        },
    ]

    for test in test_cases:
        print_separator(test["id"])
        print(f"[PREGUNTA]:\n   \"{test['query']}\"")
        print(f"\n[COMPORTAMIENTO ESPERADO]:\n   {test['expected_behavior']}")
        print("\n[EJECUCION] Ejecutando cadena RAG asincrona (Retriever -> Prompt -> LLM -> PydanticParser)...")

        try:
            rag_output = await get_rag_response(test["query"])

            print("\n[RESULTADO ESTRUCTURADO] (Pydantic RAGResponse):")
            print(f"   * Respuesta:  {rag_output.answer}")
            print(f"   * Fuentes:    {rag_output.sources}")
            print(f"   * Confianza:  {rag_output.confidence}")

            # Representación cruda JSON del modelo
            print(f"\n[JSON OUTPUT]:\n{json.dumps(rag_output.model_dump(), indent=2, ensure_ascii=False)}")

        except Exception as e:
            print(f"\n[ERROR] al ejecutar la consulta: {e}")

    print_separator("RESUMEN DE PRUEBAS COMPLETADO")


if __name__ == "__main__":
    asyncio.run(run_evaluations())

