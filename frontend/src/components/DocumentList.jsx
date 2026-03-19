import { useState } from "react";
import { deleteDocument } from "../api/ragApi";
import Modal from "./Modal";
import Toast from "./Toast";
import styles from "./DocumentList.module.css";

export default function DocumentList({ documents, onDocumentDeleted, selectedDocId, onSelectDoc }) {
  const [pendingDelete, setPendingDelete] = useState(null); // { id, filename }
  const [deletingId, setDeletingId]       = useState(null);
  const [toast, setToast]                 = useState(null); // { message, type }

  function handleDeleteClick(e, doc) {
    e.stopPropagation();
    setPendingDelete({ id: doc.document_id, filename: doc.filename });
  }

  async function confirmDelete() {
    const { id, filename } = pendingDelete;
    setPendingDelete(null);
    setDeletingId(id);

    try {
      await deleteDocument(id);
      onDocumentDeleted(id);
      setToast({ message: `"${filename}" eliminado correctamente.`, type: "success" });
    } catch (err) {
      setToast({ message: `Error al eliminar: ${err.message}`, type: "error" });
    } finally {
      setDeletingId(null);
    }
  }

  if (documents.length === 0) {
    return (
      <div className={styles.empty}>
        <p>No hay documentos indexados.</p>
        <p className={styles.hint}>Sube un archivo para empezar.</p>
      </div>
    );
  }

  return (
    <>
      <ul className={styles.list}>
        {documents.map((doc) => (
          <li
            key={doc.document_id}
            className={`${styles.item} ${selectedDocId === doc.document_id ? styles.selected : ""}`}
            onClick={() => onSelectDoc(selectedDocId === doc.document_id ? null : doc.document_id)}
            title="Clic para filtrar el chat a este documento"
          >
            <div className={styles.fileIcon}>📄</div>
            <div className={styles.info}>
              <span className={styles.filename}>{doc.filename}</span>
              <span className={styles.meta}>{doc.chunk_count} fragmentos</span>
            </div>
            <button
              className={styles.deleteBtn}
              onClick={(e) => handleDeleteClick(e, doc)}
              disabled={deletingId === doc.document_id}
              title="Eliminar documento"
            >
              {deletingId === doc.document_id ? "..." : "✕"}
            </button>
          </li>
        ))}
      </ul>

      {pendingDelete && (
        <Modal
          title="Eliminar documento"
          message={`¿Eliminar "${pendingDelete.filename}" y todos sus fragmentos indexados? Esta acción no se puede deshacer.`}
          confirmLabel="Eliminar"
          onConfirm={confirmDelete}
          onCancel={() => setPendingDelete(null)}
        />
      )}

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
