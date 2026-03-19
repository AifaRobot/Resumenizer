/**
 * ChatWindow — área principal del chat.
 *
 * Responsabilidades:
 * - Mantener el historial de mensajes (estado local)
 * - Enviar preguntas al backend
 * - Auto-scroll al último mensaje
 * - Mostrar indicador de "escribiendo..."
 */
import { useState, useRef, useEffect } from "react";
import { sendQuestion } from "../api/ragApi";
import MessageBubble from "./MessageBubble";
import styles from "./ChatWindow.module.css";

export default function ChatWindow({ selectedDocId, selectedDocName }) {
  const INITIAL_MESSAGE = {
    role: "ai",
    content: "Hola 👋 Soy tu asistente de documentos. Sube un archivo y hazme cualquier pregunta sobre su contenido.",
  };

  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll cuando llega un mensaje nuevo
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend() {
    const question = input.trim();
    if (!question || isLoading) return;

    // Añadimos el mensaje del usuario inmediatamente (UX responsiva)
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendQuestion(question, selectedDocId);

      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content: response.answer,
          sources: response.sources,
          metadata: {
            model: response.model_used,
            chunks: response.chunks_retrieved,
          },
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content: `Error: ${err.message}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleReset() {
    setMessages([INITIAL_MESSAGE]);
    setInput("");
  }

  function handleKeyDown(e) {
    // Enter envía, Shift+Enter hace salto de línea
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className={styles.container}>
      {/* Banner cuando hay un documento seleccionado */}
      {selectedDocId && (
        <div className={styles.filterBanner}>
          Filtrando por: <strong>{selectedDocName}</strong>
          <span className={styles.filterHint}>(clic en el documento para quitar filtro)</span>
        </div>
      )}

      {/* Historial de mensajes */}
      <div className={styles.messages}>
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {/* Indicador de "escribiendo" */}
        {isLoading && (
          <div className={styles.typingIndicator}>
            <span className={styles.dot} />
            <span className={styles.dot} />
            <span className={styles.dot} />
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className={styles.inputArea}>
        <button
          className={styles.resetBtn}
          onClick={handleReset}
          disabled={messages.length <= 1 || isLoading}
          title="Reiniciar conversación"
        >
          ↺
        </button>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu pregunta... (Enter para enviar)"
          rows={2}
          disabled={isLoading}
        />
        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
        >
          {isLoading ? "..." : "↑"}
        </button>
      </div>
    </div>
  );
}
