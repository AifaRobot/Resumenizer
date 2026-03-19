"""
Servicio de ingestión: orquesta el pipeline de carga de documentos.

Pipeline:
  archivo → extraer texto → chunking → embeddings → Chroma

Este servicio es la única pieza que conoce tanto el chunker como el retriever,
manteniendo los módulos RAG independientes entre sí.
"""
import uuid
import io
from pathlib import Path

from rag.chunker import chunk_text
from rag.retriever import add_document_chunks


def _extract_text_from_txt(content: bytes) -> str:
    """Decodifica un archivo de texto plano."""
    # Intentamos UTF-8 primero; si falla, Latin-1 (cubre la mayoría de textos en español)
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")


def _extract_text_from_pdf(content: bytes) -> str:
    """
    Extrae texto de un PDF usando PyPDF2.

    Limitación conocida: PDFs escaneados (imágenes) no tienen texto extraíble.
    Para esos casos se necesitaría OCR (pytesseract + pdf2image) — mejora futura.
    """
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    except Exception as e:
        raise ValueError(f"No se pudo leer el PDF: {e}")


def ingest_document(filename: str, content: bytes) -> dict:
    """
    Procesa y indexa un documento en Chroma.

    Args:
        filename: Nombre original del archivo.
        content: Bytes del archivo subido.

    Returns:
        Dict con document_id, filename, chunks_created.

    Raises:
        ValueError: Si el formato no es soportado o el archivo está vacío.
    """
    suffix = Path(filename).suffix.lower()

    # Extraemos el texto según el tipo de archivo
    if suffix == ".txt":
        text = _extract_text_from_txt(content)
    elif suffix == ".pdf":
        text = _extract_text_from_pdf(content)
    else:
        raise ValueError(f"Formato no soportado: '{suffix}'. Usa .txt o .pdf")

    if not text.strip():
        raise ValueError("El documento está vacío o no contiene texto extraíble.")

    # Chunking: dividimos el texto en fragmentos con overlap
    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("No se pudieron generar chunks del documento.")

    # Generamos un ID único para este documento
    document_id = str(uuid.uuid4())

    # Indexamos en Chroma (genera embeddings + guarda en disco)
    chunks_created = add_document_chunks(
        document_id=document_id,
        filename=filename,
        chunks=chunks,
    )

    return {
        "document_id": document_id,
        "filename": filename,
        "chunks_created": chunks_created,
    }
