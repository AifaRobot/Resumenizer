/**
 * App — componente raíz y layout principal.
 *
 * Layout de dos paneles:
 * ┌─────────────┬──────────────────────────────┐
 * │   Sidebar   │       Chat Window             │
 * │  (docs)     │                               │
 * └─────────────┴──────────────────────────────┘
 *
 * Estado global mínimo aquí:
 * - Lista de documentos (se pasa como prop a los hijos)
 * - Documento seleccionado para filtrar el chat
 */
import { useState, useEffect } from "react";
import { listDocuments } from "./api/ragApi";
import DocumentUploader from "./components/DocumentUploader";
import DocumentList from "./components/DocumentList";
import ChatWindow from "./components/ChatWindow";
import styles from "./App.module.css";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [loadingDocs, setLoadingDocs] = useState(true);

  // Cargamos los documentos al montar
  useEffect(() => {
    fetchDocuments();
  }, []);

  async function fetchDocuments() {
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
    } catch (err) {
      console.error("Error cargando documentos:", err);
    } finally {
      setLoadingDocs(false);
    }
  }

  function handleDocumentUploaded(uploadResult) {
    // Añadimos el nuevo documento sin refetch completo
    setDocuments((prev) => [
      ...prev,
      {
        document_id: uploadResult.document_id,
        filename: uploadResult.filename,
        chunk_count: uploadResult.chunks_created,
      },
    ]);
  }

  function handleDocumentDeleted(documentId) {
    setDocuments((prev) => prev.filter((d) => d.document_id !== documentId));
    // Si el doc eliminado era el seleccionado, limpiamos la selección
    if (selectedDocId === documentId) setSelectedDocId(null);
  }

  const selectedDoc = documents.find((d) => d.document_id === selectedDocId);

  return (
    <div className={styles.layout}>
      {/* ─── Sidebar ──────────────────────────────────── */}
      <aside className={styles.sidebar}>
        <header className={styles.sidebarHeader}>
          <h1 className={styles.logo}>📚 Resumenizer</h1>
          <p className={styles.tagline}>Chat con tus documentos</p>
        </header>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Subir documento</h2>
          <DocumentUploader onDocumentUploaded={handleDocumentUploaded} />
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>
            Documentos indexados
            {documents.length > 0 && (
              <span className={styles.badge}>{documents.length}</span>
            )}
          </h2>
          {loadingDocs ? (
            <p className={styles.loading}>Cargando...</p>
          ) : (
            <DocumentList
              documents={documents}
              onDocumentDeleted={handleDocumentDeleted}
              selectedDocId={selectedDocId}
              onSelectDoc={setSelectedDocId}
            />
          )}
        </section>

        <footer className={styles.sidebarFooter}>
          <p>
            {selectedDocId
              ? `Filtrando: ${selectedDoc?.filename}`
              : "Buscando en todos los documentos"}
          </p>
        </footer>
      </aside>

      {/* ─── Chat ─────────────────────────────────────── */}
      <main className={styles.main}>
        <ChatWindow
          selectedDocId={selectedDocId}
          selectedDocName={selectedDoc?.filename}
        />
      </main>
    </div>
  );
}
