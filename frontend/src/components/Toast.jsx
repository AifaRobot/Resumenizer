import { useEffect } from "react";
import styles from "./Toast.module.css";

/**
 * Toast — notificación temporal que se auto-cierra.
 *
 * Props:
 *   message: texto a mostrar
 *   type: "success" | "error"
 *   onClose: callback cuando se cierra (por timeout o por el usuario)
 */
export default function Toast({ message, type = "success", onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3500);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`${styles.toast} ${styles[type]}`}>
      <span className={styles.icon}>{type === "success" ? "✓" : "✕"}</span>
      <span className={styles.message}>{message}</span>
      <button className={styles.closeBtn} onClick={onClose}>✕</button>
    </div>
  );
}
