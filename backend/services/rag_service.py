"""
Servicio RAG: orquesta el pipeline completo de consulta.

Pipeline:
  pregunta → embedding query → búsqueda semántica → construcción contexto → LLM → respuesta

Este servicio conecta retriever + generator, manteniéndolos desacoplados.
Las rutas solo llaman a este servicio — no conocen los detalles de Chroma ni OpenAI.
"""
from config import settings
from rag.retriever import search_similar_chunks
from rag.generator import generate_answer
from models.schemas import ChatResponse, SourceChunk


def answer_question(
    question: str,
    document_id: str = None,
    top_k: int = None,
) -> ChatResponse:
    """
    Ejecuta el pipeline RAG completo para una pregunta.

    Args:
        question: Pregunta del usuario.
        document_id: Filtrar búsqueda a un documento específico (opcional).
        top_k: Cuántos chunks recuperar (usa el default de settings si no se provee).

    Returns:
        ChatResponse con la respuesta y las fuentes utilizadas.
    """
    effective_top_k = top_k or settings.top_k

    # 1. RETRIEVAL: buscamos los chunks más relevantes semánticamente
    chunks = search_similar_chunks(
        query=question,
        top_k=effective_top_k,
        document_id=document_id,
    )

    # 2. GENERATION: el LLM genera la respuesta usando los chunks como contexto
    answer = generate_answer(question=question, context_chunks=chunks)

    # 3. Construimos la respuesta estructurada para la API
    sources = [
        SourceChunk(
            document_id=chunk["document_id"],
            filename=chunk["filename"],
            content=chunk["content"],
            relevance_score=chunk["relevance_score"],
        )
        for chunk in chunks
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
        model_used=settings.chat_model,
        chunks_retrieved=len(chunks),
    )
