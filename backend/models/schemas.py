"""
Modelos Pydantic para requests y responses de la API.
Separar los schemas de los modelos de dominio permite versionar la API
sin romper la lógica interna.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── Documentos ──────────────────────────────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    message: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    created_at: Optional[str] = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


# ─── Chat / RAG ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    # Permitir filtrar por documento específico (opcional)
    document_id: Optional[str] = None
    # Cuántos chunks recuperar (override del default)
    top_k: Optional[int] = Field(None, ge=1, le=20)


class SourceChunk(BaseModel):
    """Fragmento de documento recuperado para fundamentar la respuesta."""
    document_id: str
    filename: str
    content: str
    # Score de similitud coseno (1.0 = idéntico, 0.0 = sin relación)
    relevance_score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    # Metadata útil para debugging / UI
    model_used: str
    chunks_retrieved: int


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    chroma_collection: str
    documents_indexed: int
