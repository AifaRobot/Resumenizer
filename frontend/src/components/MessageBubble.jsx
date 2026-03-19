/**
 * MessageBubble — renderiza un mensaje del chat (usuario o IA).
 *
 * Para mensajes de IA, también muestra las fuentes colapsables
 * para que el usuario pueda verificar de dónde viene la información.
 */
import { useState } from "react";
import styles from "./MessageBubble.module.css";

export default function MessageBubble({ message }) {
  const { role, content, sources } = message;
  const isUser = role === "user";
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <div className={`${styles.wrapper} ${isUser ? styles.userWrapper : styles.aiWrapper}`}>
      <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.aiBubble}`}>
        {/* Avatar */}
        <span className={styles.avatar}>{isUser ? "👤" : "🤖"}</span>

        <div className={styles.content}>
          {/* Texto del mensaje */}
          <p className={styles.text}>{content}</p>

          {/* Fuentes — solo para mensajes de IA con sources */}
          {!isUser && sources && sources.length > 0 && (
            <div className={styles.sourcesContainer}>
              <button
                className={styles.sourcesToggle}
                onClick={() => setSourcesOpen(!sourcesOpen)}
              >
                {sourcesOpen ? "▾" : "▸"} {sources.length} fuente{sources.length > 1 ? "s" : ""}
              </button>

              {sourcesOpen && (
                <ul className={styles.sourcesList}>
                  {sources.map((src, i) => (
                    <li key={i} className={styles.sourceItem}>
                      <div className={styles.sourceHeader}>
                        <span className={styles.sourceFile}>📄 {src.filename}</span>
                        <span className={styles.sourceScore}>
                          {Math.round(src.relevance_score * 100)}% relevancia
                        </span>
                      </div>
                      <p className={styles.sourceText}>
                        {src.content.slice(0, 200)}
                        {src.content.length > 200 ? "..." : ""}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
