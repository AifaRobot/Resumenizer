"""
Punto de entrada de la aplicación FastAPI.

Estructura:
  - CORS configurado para desarrollo local (React en puerto 5173)
  - Rutas montadas bajo /api/v1 para versionado
  - Health check en /health
  - Manejo global de errores de validación
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from routes import documents, chat
from rag.retriever import get_collection_stats
from models.schemas import HealthResponse

app = FastAPI(
    title="Resumenizer API",
    description="Sistema RAG: Chat con tus documentos usando IA",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI disponible en desarrollo
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# En producción, reemplaza "*" por el dominio real del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Rutas ────────────────────────────────────────────────────────────────────
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check():
    """
    Verifica el estado del sistema y la conexión con Chroma.
    Útil para monitoreo y para que el frontend sepa si el backend está activo.
    """
    try:
        stats = get_collection_stats()
        return HealthResponse(
            status="ok",
            chroma_collection=stats["collection_name"],
            documents_indexed=stats["total_documents"],
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": str(e)},
        )


# ─── Manejo global de errores de validación ───────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Devuelve errores de validación Pydantic en formato legible."""
    errors = [
        {"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": "Error de validación", "errors": errors},
    )


# ─── Inicio ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    # reload=True para desarrollo: recarga automática al cambiar archivos
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
