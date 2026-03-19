"""
Módulo de generación: construye el prompt y llama al LLM para generar respuesta.

Decisión de diseño del prompt:
- Instrucción clara de rol (asistente especializado)
- Contexto delimitado con etiquetas XML → más fácil de parsear para el modelo
- Instrucción explícita de citar fuentes → reduce alucinaciones
- Instrucción de responder "no sé" si el contexto no es suficiente
  → preferimos honestidad a inventar información

Usamos gpt-4o-mini: buena calidad, muy bajo costo (~$0.15/1M input tokens).
"""
from openai import OpenAI
from config import settings

_client = OpenAI(api_key=settings.openai_api_key)

# Prompt del sistema: establece el comportamiento del asistente
SYSTEM_PROMPT = """Eres un asistente experto en análisis de documentos.
Tu tarea es responder preguntas del usuario basándote ÚNICAMENTE en el contexto proporcionado.

Reglas:
1. Responde siempre en el mismo idioma que la pregunta del usuario.
2. Si la respuesta está en el contexto, responde de forma clara y concisa.
3. Si el contexto no contiene información suficiente para responder, di exactamente:
   "No encontré información suficiente en los documentos para responder esa pregunta."
4. No inventes información. No uses conocimiento externo al contexto.
5. Cuando cites información, menciona el documento fuente si es relevante.
"""


def build_context(chunks: list[dict]) -> str:
    """
    Construye el bloque de contexto a partir de los chunks recuperados.

    Formato elegido: XML-like tags para delimitar claramente cada fragmento.
    Esto ayuda al modelo a distinguir entre múltiples fuentes.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"<fragmento_{i} fuente=\"{chunk['filename']}\">\n"
            f"{chunk['content']}\n"
            f"</fragmento_{i}>"
        )
    return "\n\n".join(context_parts)


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    """
    Genera una respuesta usando el LLM con los chunks como contexto.

    Args:
        question: Pregunta original del usuario.
        context_chunks: Lista de chunks recuperados por el retriever.

    Returns:
        Respuesta generada por el modelo como string.
    """
    if not context_chunks:
        return "No encontré información suficiente en los documentos para responder esa pregunta."

    context = build_context(context_chunks)

    # Prompt de usuario: combina contexto + pregunta
    user_message = f"""<contexto>
{context}
</contexto>

<pregunta>
{question}
</pregunta>"""

    response = _client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,      # bajo temperatura → respuestas más deterministas y fieles al contexto
        max_tokens=1024,      # suficiente para respuestas detalladas sin disparar el costo
    )

    return response.choices[0].message.content.strip()
