/**
 * DocumentUploader — zona de drag & drop + botón para subir archivos.
 *
 * Responsabilidades:
 * - Validar formato y tamaño antes de enviar
 * - Mostrar progreso de subida
 * - Notificar al padre cuando el documento fue indexado exitosamente
 */
import { useState, useRef } from "react";
import { uploadDocument } from "../api/ragApi";
import Toast from "./Toast";
import styles from "./DocumentUploader.module.css";

const MAX_SIZE_MB = 10;
const ALLOWED_TYPES = [".txt", ".pdf"];

export default function DocumentUploader({ onDocumentUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);
  const inputRef = useRef(null);

  function validateFile(file) {
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_TYPES.includes(ext)) {
      return `Formato no soportado. Usa: ${ALLOWED_TYPES.join(", ")}`;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `El archivo supera el límite de ${MAX_SIZE_MB} MB`;
    }
    return null;
  }

  async function handleFile(file) {
    setError(null);
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsUploading(true);
    setProgress(0);

    try {
      const result = await uploadDocument(file, setProgress);
      onDocumentUploaded(result);
      setToast({ message: `"${result.filename}" indexado correctamente.`, type: "success" });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
      setProgress(0);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function handleInputChange(e) {
    const file = e.target.files[0];
    if (file) handleFile(file);
    // Reset input para permitir subir el mismo archivo de nuevo
    e.target.value = "";
  }

  return (
    <>
    <div
      className={`${styles.dropzone} ${isDragging ? styles.dragging : ""} ${isUploading ? styles.uploading : ""}`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => !isUploading && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".txt,.pdf"
        onChange={handleInputChange}
        style={{ display: "none" }}
      />

      {isUploading ? (
        <div className={styles.progressContainer}>
          <span className={styles.uploadingText}>Indexando documento...</span>
          <div className={styles.progressBar}>
            <div className={styles.progressFill} style={{ width: `${progress}%` }} />
          </div>
          <span className={styles.progressText}>{progress}%</span>
        </div>
      ) : (
        <>
          <div className={styles.icon}>📄</div>
          <p className={styles.hint}>
            Arrastra un archivo aquí o <span className={styles.link}>selecciona uno</span>
          </p>
          <p className={styles.formats}>TXT, PDF · Máx {MAX_SIZE_MB} MB</p>
        </>
      )}

      {error && <p className={styles.error}>{error}</p>}
    </div>

    {toast && (
      <Toast
        message={toast.message}
        type={toast.type}
        onClose={() => setToast(null)}
      />
    )}
    </>
  );
}
