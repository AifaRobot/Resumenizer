"""
Configuración centralizada del proyecto.
Usa pydantic-settings para leer variables de entorno desde .env
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    # Modelos
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    # Chroma
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "documents"

    # Chunking
    chunk_size: int = 400        # tokens por chunk
    chunk_overlap: int = 50      # tokens de overlap entre chunks

    # Retrieval
    top_k: int = 5               # número de chunks a recuperar

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton: se importa desde cualquier módulo
settings = Settings()
