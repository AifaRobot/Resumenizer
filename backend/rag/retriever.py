"""
Módulo de retrieval: gestiona la colección Chroma y las búsquedas semánticas.

Chroma persiste los datos en disco (CHROMA_PERSIST_DIR), lo que significa que
los documentos indexados sobreviven reinicios del servidor — no hace falta
re-indexar cada vez que arranca la app.

Decisión de diseño: usamos embeddings propios (embed_texts) en lugar del
EmbeddingFunction de Chroma, para tener control total sobre los parámetros
del modelo y poder cachear / batchar las llamadas a OpenAI.
"""
import uuid
import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings
from rag.embedder import embed_texts, embed_query


def _get_collection():
    """
    Inicializa el cliente Chroma y devuelve la colección.

    Usamos PersistentClient para que los datos se guarden en disco.
    Se crea la colección si no existe — idempotente.
    """
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    # get_or_create evita errores si la colección ya existe
    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        # distance: cosine es la métrica estándar para text embeddings
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def add_document_chunks(
    document_id: str,
    filename: str,
    chunks: list[str],
) -> int:
    """
    Indexa los chunks de un documento en Chroma.

    Genera los embeddings en batch y los almacena junto con metadata
    que permite filtrar por documento o recuperar la fuente después.

    Args:
        document_id: ID único del documento (para filtros y trazabilidad).
        filename: Nombre del archivo original (para mostrar en la UI).
        chunks: Lista de strings a indexar.

    Returns:
        Número de chunks insertados.
    """
    if not chunks:
        return 0

    collection = _get_collection()

    # Generamos embeddings en batch — una sola llamada a OpenAI
    embeddings = embed_texts(chunks)

    # Cada chunk necesita un ID único dentro de la colección
    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

    # Metadata almacenada junto al vector — usada para filtros y fuentes
    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)


def search_similar_chunks(
    query: str,
    top_k: int = None,
    document_id: str = None,
) -> list[dict]:
    """
    Busca los chunks más similares semánticamente a la query.

    Args:
        query: Pregunta del usuario.
        top_k: Cuántos chunks recuperar.
        document_id: Si se provee, filtra resultados a un solo documento.

    Returns:
        Lista de dicts con keys: document_id, filename, content, relevance_score.
    """
    top_k = top_k or settings.top_k
    collection = _get_collection()

    # Verificamos que hay datos en la colección antes de consultar
    if collection.count() == 0:
        return []

    # Embeddimos la query con el mismo modelo usado en la indexación
    # (mismo modelo = mismo espacio vectorial = búsqueda válida)
    query_vector = embed_query(query)

    # Filtro opcional por documento
    where_filter = {"document_id": document_id} if document_id else None

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),  # evita pedir más de lo que hay
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # Chroma con cosine devuelve distancia (0=idéntico, 2=opuesto)
        # Convertimos a score de relevancia: 1 - distancia/2 → [0, 1]
        relevance_score = round(1 - (distance / 2), 4)

        chunks.append({
            "document_id": meta["document_id"],
            "filename": meta["filename"],
            "content": doc,
            "relevance_score": relevance_score,
        })

    return chunks


def delete_document(document_id: str) -> int:
    """
    Elimina todos los chunks de un documento de Chroma.

    Returns:
        Número de chunks eliminados.
    """
    collection = _get_collection()

    # Primero obtenemos los IDs de los chunks de ese documento
    results = collection.get(
        where={"document_id": document_id},
        include=[],  # solo necesitamos los IDs
    )

    if not results["ids"]:
        return 0

    collection.delete(ids=results["ids"])
    return len(results["ids"])


def get_collection_stats() -> dict:
    """Devuelve estadísticas básicas de la colección (útil para /health)."""
    collection = _get_collection()
    count = collection.count()

    # Obtenemos documentos únicos contando document_ids distintos
    if count > 0:
        all_meta = collection.get(include=["metadatas"])
        doc_ids = {m["document_id"] for m in all_meta["metadatas"]}
    else:
        doc_ids = set()

    return {
        "total_chunks": count,
        "total_documents": len(doc_ids),
        "collection_name": settings.chroma_collection_name,
    }
