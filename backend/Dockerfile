FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias del sistema necesarias para chromadb y PyPDF2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements primero para aprovechar la caché de capas de Docker.
# Si el código cambia pero requirements.txt no, esta capa no se reconstruye.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# reload=False en producción — en Docker los cambios no son "en caliente"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
