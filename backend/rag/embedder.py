"""
Módulo de embeddings: convierte texto en vectores usando OpenAI.

Usamos text-embedding-3-small por su excelente balance precio/calidad.
Dimensiones: 1536. Costo: ~$0.02 / millón de tokens.

Decisión de diseño: este módulo es stateless — no guarda nada en Chroma,
solo genera vectores. La persistencia es responsabilidad del retriever.
"""
from openai import OpenAI
from config import settings

# Cliente OpenAI — se inicializa una vez por proceso
_client = OpenAI(api_key=settings.openai_api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Genera embeddings para una lista de textos.

    Enviamos todos los textos en una sola llamada a la API (batch)
    para minimizar latencia y costo. La API de OpenAI soporta hasta
    2048 inputs por request.

    Args:
        texts: Lista de strings a embeddir.

    Returns:
        Lista de vectores (list[float]) en el mismo orden que los inputs.
    """
    if not texts:
        return []

    # Limpiamos textos vacíos — la API los rechaza
    cleaned = [t.strip().replace("\n", " ") for t in texts if t.strip()]

    response = _client.embeddings.create(
        model=settings.embedding_model,
        input=cleaned,
    )

    # La API devuelve los embeddings ordenados por índice
    return [item.embedding for item in response.data]


def embed_query(query: str) -> list[float]:
    """
    Genera el embedding de una consulta del usuario.

    Wrapper conveniente sobre embed_texts para el caso más común (1 texto).
    """
    vectors = embed_texts([query])
    if not vectors:
        raise ValueError("No se pudo generar embedding para la consulta.")
    return vectors[0]
