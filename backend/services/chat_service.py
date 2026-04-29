# chat_service.py - Manages chat sessions and generates AI responses
# Handles session memory so the AI remembers conversation history

from models.database import get_connection
from services.groq_client import chat_with_groq, get_system_prompt
from services.rag_service import build_rag_context, retrieve_relevant_knowledge


def get_session_history(session_id: str, limit: int = 10) -> list:
    """
    Fetch the last N messages from the database for a session.
    This gives the AI memory of the conversation.

    Args:
        session_id: Unique identifier for the chat session
        limit: How many past messages to include

    Returns:
        List of message dicts with role and content
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content FROM chat_sessions
        WHERE session_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (session_id, limit))

    rows = cursor.fetchall()
    conn.close()

    # Reverse so oldest messages come first (correct order for LLM)
    messages = [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]
    return messages


def save_message(session_id: str, role: str, content: str):
    """
    Save a single message to the database.

    Args:
        session_id: The chat session ID
        role: Either "user" or "assistant"
        content: The message text
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_sessions (session_id, role, content)
        VALUES (?, ?, ?)
    """, (session_id, role, content))

    conn.commit()
    conn.close()


def generate_chat_response(session_id: str, user_message: str) -> dict:
    """
    Main function to generate an AI response for a user message.
    Steps:
        1. Fetch past conversation history (memory)
        2. Retrieve relevant knowledge using RAG
        3. Build the full prompt with context
        4. Call Groq LLM
        5. Save both messages to database
        6. Return the response

    Args:
        session_id: Unique chat session ID
        user_message: The user's latest message

    Returns:
        Dict with reply text and RAG sources used
    """

    # Step 1 - Get conversation history for memory
    history = get_session_history(session_id, limit=10)

    # Step 2 - Get relevant knowledge from RAG
    rag_context = build_rag_context(user_message)
    sources = retrieve_relevant_knowledge(user_message, top_k=2)
    source_topics = [s["topic"] for s in sources]

    # Step 3 - Build the messages list for Groq
    # Format: [system prompt, ...history, optional RAG context, user message]
    messages = [
        {"role": "system", "content": get_system_prompt("career_assistant")}
    ]

    # Add conversation history
    messages.extend(history)

    # If RAG found relevant context, inject it before the user message
    if rag_context:
        messages.append({
            "role": "system",
            "content": rag_context
        })

    # Add the current user message
    messages.append({"role": "user", "content": user_message})

    # Step 4 - Call Groq LLM
    reply = chat_with_groq(messages, temperature=0.7, max_tokens=1024)

    # Step 5 - Save both messages to database for future memory
    save_message(session_id, "user", user_message)
    save_message(session_id, "assistant", reply)

    # Step 6 - Return response
    return {
        "reply": reply,
        "sources": source_topics
    }