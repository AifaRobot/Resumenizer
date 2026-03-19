/**
 * Capa de abstracción para comunicación con el backend.
 *
 * Centralizar las llamadas a la API aquí significa que si cambia
 * la URL base o la versión de la API, solo hay que modificar este archivo.
 */
import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 60000, // 60s — las llamadas a OpenAI pueden tardar
});

// ─── Interceptor global de errores ──────────────────────────────────────────
// Normaliza los errores para que los componentes siempre reciban un string
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "Error desconocido";
    return Promise.reject(new Error(message));
  }
);

// ─── Documentos ──────────────────────────────────────────────────────────────

/**
 * Sube un archivo al backend para ser indexado.
 * @param {File} file - Archivo seleccionado por el usuario
 * @param {Function} onProgress - Callback con porcentaje de progreso (0-100)
 */
export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await api.post("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    },
  });

  return data; // { document_id, filename, chunks_created, message }
}

/**
 * Lista todos los documentos indexados.
 */
export async function listDocuments() {
  const { data } = await api.get("/documents/");
  return data; // { documents: [...], total }
}

/**
 * Elimina un documento y sus chunks de Chroma.
 * @param {string} documentId
 */
export async function deleteDocument(documentId) {
  const { data } = await api.delete(`/documents/${documentId}`);
  return data;
}

// ─── Chat ────────────────────────────────────────────────────────────────────

/**
 * Envía una pregunta y recibe la respuesta RAG.
 * @param {string} question - Pregunta del usuario
 * @param {string|null} documentId - Filtrar a un documento específico (opcional)
 */
export async function sendQuestion(question, documentId = null) {
  const { data } = await api.post("/chat/", {
    question,
    document_id: documentId || undefined,
  });
  return data; // { answer, sources, model_used, chunks_retrieved }
}

// ─── Health ───────────────────────────────────────────────────────────────────

export async function checkHealth() {
  const { data } = await axios.get("/health");
  return data;
}
