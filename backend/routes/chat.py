"""
Rutas del chat / RAG.

Endpoints:
  POST /chat/  → recibe una pregunta y devuelve respuesta + fuentes
"""
from fastapi import APIRouter, HTTPException

from services.rag_service import answer_question
from models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Ejecuta el pipeline RAG completo:
    1. Embedding de la query
    2. Búsqueda semántica en Chroma
    3. Construcción del prompt con contexto
    4. Generación de respuesta con GPT

    Body:
        question: Pregunta del usuario (requerido)
        document_id: ID del documento a consultar (opcional, filtra la búsqueda)
        top_k: Número de fragmentos a recuperar (opcional, default: settings.TOP_K)
    """
    try:
        response = answer_question(
            question=request.question,
            document_id=request.document_id,
            top_k=request.top_k,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la consulta: {str(e)}",
        )
