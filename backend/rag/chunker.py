"""
Módulo de chunking: divide documentos largos en fragmentos manejables.

Estrategia: sliding window por tokens usando tiktoken.
- chunk_size: máximo de tokens por chunk
- chunk_overlap: tokens que se repiten entre chunks consecutivos
  → el overlap es clave para no perder contexto en los bordes de los chunks.
"""
import tiktoken
from config import settings


# Cargamos el tokenizer una sola vez (es costoso instanciar)
# cl100k_base es el tokenizer de text-embedding-3-* y gpt-4o
_tokenizer = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    """
    Divide un texto en chunks de tamaño máximo `chunk_size` tokens,
    con `overlap` tokens de solapamiento entre chunks consecutivos.

    Args:
        text: Texto completo a dividir.
        chunk_size: Tokens máximos por chunk (default: settings.chunk_size).
        overlap: Tokens de overlap (default: settings.chunk_overlap).

    Returns:
        Lista de strings (chunks de texto).
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    if not text or not text.strip():
        return []

    # Tokenizamos el texto completo una sola vez
    tokens = _tokenizer.encode(text)

    if len(tokens) <= chunk_size:
        # El texto cabe en un solo chunk — no hace falta dividir
        return [text]

    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]

        # Decodificamos de vuelta a texto (errors='replace' evita crashes con tokens especiales)
        chunk_text_decoded = _tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text_decoded)

        if end == len(tokens):
            break

        # Avanzamos restando el overlap para que el siguiente chunk
        # comience un poco antes del final del actual
        start += chunk_size - overlap

    return chunks


def count_tokens(text: str) -> int:
    """Devuelve el número de tokens de un texto. Útil para logging y validación."""
    return len(_tokenizer.encode(text))
