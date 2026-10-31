"""
Esquemas de datos Pydantic para la respuesta estructurada de la cadena RAG.
"""

from typing import List
from pydantic import BaseModel, Field


class RAGResponse(BaseModel):
    """
    Modelo Pydantic para estructurar la respuesta final generada por el sistema RAG.
    Garantiza que el LLM devuelva tanto la respuesta textual como las fuentes
    documentales utilizadas y el nivel de certeza del contexto.
    """
    answer: str = Field(
        description=(
            "Respuesta directa y precisa a la pregunta del usuario basada EXCLUSIVAMENTE "
            "en el contexto suministrado. Si la información no está en el contexto, debe "
            "indicar explícitamente: 'No lo sé' o 'No dispongo de información suficiente en el contexto'."
        )
    )
    sources: List[str] = Field(
        default_factory=list,
        description=(
            "Lista de nombres o rutas de los documentos de origen de los fragmentos "
            "utilizados para fundamentar la respuesta (ej. ['01_manual_seguridad_accesos.md']). "
            "Si la información no estaba en el contexto, debe ser una lista vacía []."
        )
    )
    confidence: str = Field(
        default="HIGH",
        description=(
            "Nivel de confianza de la respuesta según el contexto disponible. "
            "Opciones: 'HIGH', 'MEDIUM', 'LOW' o 'INSUFFICIENT_CONTEXT'."
        )
    )

