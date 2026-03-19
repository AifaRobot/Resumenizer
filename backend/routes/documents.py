"""
Rutas para gestión de documentos.

Endpoints:
  POST /documents/upload  → sube e indexa un documento
  GET  /documents/        → lista los documentos indexados
  DELETE /documents/{id}  → elimina un documento y sus chunks
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from services.ingestion_service import ingest_document
from rag.retriever import get_collection_stats, delete_document, _get_collection
from models.schemas import DocumentUploadResponse, DocumentListResponse, DocumentInfo

router = APIRouter(prefix="/documents", tags=["documents"])

# Tamaño máximo de archivo: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".pdf"}


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Sube un documento, lo chunka, genera embeddings y lo indexa en Chroma.

    Formatos aceptados: .txt, .pdf
    Tamaño máximo: 10 MB
    """
    # Validación básica del nombre del archivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo no tiene nombre.")

    from pathlib import Path
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: '{suffix}'. Formatos aceptados: {ALLOWED_EXTENSIONS}",
        )

    # Leemos el contenido del archivo
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo supera el límite de {MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    try:
        result = ingest_document(filename=file.filename, content=content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Capturamos errores de OpenAI / Chroma y devolvemos 500
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el documento: {str(e)}",
        )

    return DocumentUploadResponse(
        document_id=result["document_id"],
        filename=result["filename"],
        chunks_created=result["chunks_created"],
        message=f"Documento indexado correctamente en {result['chunks_created']} fragmentos.",
    )


@router.get("/", response_model=DocumentListResponse)
def list_documents():
    """
    Lista todos los documentos indexados con su conteo de chunks.
    """
    collection = _get_collection()

    if collection.count() == 0:
        return DocumentListResponse(documents=[], total=0)

    # Obtenemos todos los metadatos para agrupar por documento
    all_data = collection.get(include=["metadatas"])

    # Agrupamos chunks por documento
    doc_map: dict[str, DocumentInfo] = {}
    for meta in all_data["metadatas"]:
        doc_id = meta["document_id"]
        if doc_id not in doc_map:
            doc_map[doc_id] = DocumentInfo(
                document_id=doc_id,
                filename=meta["filename"],
                chunk_count=0,
            )
        doc_map[doc_id].chunk_count += 1

    documents = list(doc_map.values())
    return DocumentListResponse(documents=documents, total=len(documents))


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def remove_document(document_id: str):
    """
    Elimina un documento y todos sus chunks de Chroma.
    """
    deleted_count = delete_document(document_id)

    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró ningún documento con ID '{document_id}'.",
        )

    return {
        "message": f"Documento eliminado. Se borraron {deleted_count} fragmentos.",
        "document_id": document_id,
        "chunks_deleted": deleted_count,
    }
