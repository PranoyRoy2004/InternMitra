# chat.py - API endpoints for the chat assistant
# Handles incoming chat requests and returns AI responses

from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from services.chat_service import generate_chat_response

# APIRouter groups related endpoints together
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Main chat endpoint.
    Receives a message from the user and returns an AI response.
    
    Example request body:
    {
        "session_id": "user123-session1",
        "message": "How do I prepare for a Python internship interview?",
        "user_id": "user123"
    }
    """
    try:
        result = generate_chat_response(
            session_id=request.session_id,
            user_message=request.message
        )

        return ChatResponse(
            session_id=request.session_id,
            reply=result["reply"],
            sources=result["sources"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Returns the full chat history for a session.
    Useful for restoring chat on page reload.
    """
    try:
        from services.chat_service import get_session_history
        history = get_session_history(session_id, limit=50)
        return {"session_id": session_id, "history": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History error: {str(e)}")


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clears the chat history for a session.
    Called when user clicks 'New Chat'.
    """
    try:
        from models.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return {"message": f"Chat history cleared for session {session_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear error: {str(e)}")