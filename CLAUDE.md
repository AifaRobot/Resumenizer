# CLAUDE.md — Guía para Claude Code

Este archivo describe el proyecto y las convenciones para que Claude Code trabaje eficientemente en este repositorio.

---

## Qué es este proyecto

**Resumenizer** es una aplicación web de RAG (Retrieval-Augmented Generation) que permite subir documentos (.txt, .pdf) y hacerles preguntas en lenguaje natural. La IA responde basándose exclusivamente en el contenido de los archivos subidos, citando las fuentes exactas.

---

## Arquitectura

```
Frontend (React + Vite) ──► Nginx ──► Backend (FastAPI) ──► ChromaDB (vectores)
                                                         └──► OpenAI API (embeddings + chat)
```

- **Frontend**: React 18 + Vite, servido por Nginx en producción. Nginx también hace proxy de `/api` al backend.
- **Backend**: FastAPI con tres capas: `routes/` → `services/` → `rag/`.
- **ChromaDB**: base de datos vectorial persistida en `./db/` (montada como volumen Docker).
- **Variables de entorno**: definidas en `.env` (raíz del proyecto), consumidas por el backend vía `backend/config.py`.

---

## Comandos frecuentes

### Docker (recomendado)
```bash
docker compose up --build        # Levantar todo (build incluido)
docker compose up                # Levantar sin rebuild
docker compose down              # Apagar
docker compose logs -f backend   # Ver logs del backend
```

### Backend (desarrollo local)
```bash
cd backend
python -m venv venv
venv/Scripts/activate            # Windows
pip install -r requirements.txt
python main.py                   # http://localhost:8000
```

### Frontend (desarrollo local)
```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
npm run build                    # Build de producción
```

---

## Archivos clave

| Archivo | Responsabilidad |
|---------|----------------|
| `backend/main.py` | Punto de entrada FastAPI: CORS, routers, health check |
| `backend/config.py` | Variables de entorno con `pydantic-settings` |
| `backend/rag/chunker.py` | Fragmenta texto en chunks de ~400 tokens (tiktoken) |
| `backend/rag/embedder.py` | Genera embeddings con `text-embedding-3-small` (batch) |
| `backend/rag/retriever.py` | ChromaDB: añadir, buscar por similitud, eliminar |
| `backend/rag/generator.py` | Construye el prompt y llama a `gpt-4o-mini` |
| `backend/services/ingestion_service.py` | Orquesta: archivo → chunks → embeddings → ChromaDB |
| `backend/services/rag_service.py` | Orquesta: pregunta → retrieval → prompt → respuesta |
| `backend/routes/documents.py` | Rutas: `POST /upload`, `GET /`, `DELETE /{id}` |
| `backend/routes/chat.py` | Ruta: `POST /chat/` |
| `backend/models/schemas.py` | Modelos Pydantic de request/response |
| `frontend/src/api/ragApi.js` | Toda la comunicación HTTP con el backend |
| `frontend/src/App.jsx` | Estado global + layout de dos paneles |
| `frontend/nginx.conf` | Proxy `/api` → backend + sirve estáticos |
| `docker-compose.yml` | Orquestación: backend + frontend, volumen de ChromaDB |

---

## Variables de entorno

Copiar `.env.example` a `.env` y completar:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API key de OpenAI | *(requerido)* |
| `CHROMA_PERSIST_DIR` | Directorio de ChromaDB | `./chroma_db` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `text-embedding-3-small` |
| `CHAT_MODEL` | Modelo de chat | `gpt-4o-mini` |
| `CHUNK_SIZE` | Tamaño de chunk en tokens | `400` |
| `CHUNK_OVERLAP` | Solapamiento entre chunks | `50` |
| `TOP_K` | Fragmentos a recuperar por query | `5` |

---

## Convenciones

- **Idioma**: código en inglés, comentarios y nombres de variables de dominio en español cuando tiene sentido (ej. `documentos`).
- **Backend**: seguir la separación de capas existente — no poner lógica de negocio en `routes/`, delegarla a `services/`.
- **Frontend**: estado en `App.jsx`, comunicación HTTP solo en `ragApi.js`, componentes en `components/`.
- **No commitear**: `.env`, `db/`, `chroma_db/`, `node_modules/`, `__pycache__/`.
- **API prefix**: todas las rutas del backend van bajo `/api/v1/`.

---

## Flujo de datos resumido

**Subir documento:**
```
POST /api/v1/documents/upload
  → ingestion_service: extrae texto → chunker → embedder → retriever.add()
```

**Hacer una pregunta:**
```
POST /api/v1/chat/
  → rag_service: embedder(pregunta) → retriever.search() → generator(chunks + pregunta)
  ← { answer, sources, model_used, chunks_retrieved }
```
