# main.py - The entry point of the InternMitra backend
# This is where FastAPI is initialized and all routes are connected

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file first
load_dotenv()

# Import database initializer
from models.database import init_db

# Import all route routers
from routes.chat import router as chat_router
from routes.recommendations import router as recommendations_router
from routes.tracker import router as tracker_router
from routes.evaluation import router as evaluation_router

# ── Initialize FastAPI app ────────────────────────────────────────────────────
app = FastAPI(
    title="InternMitra API",
    description="AI-powered internship assistant backend",
    version="1.0.0"
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
# This allows the frontend (running on a different port) to talk to the backend
# In production, replace "*" with your actual frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://heroic-stardust-3776f9.netlify.app",
                   "http://localhost:5500",
                   "http://127.0.0.1:5500",
                    "http://127.0.0.1:3000"
    ],        # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],        # Allow GET, POST, PUT, DELETE etc.
    allow_headers=["*"],
)

# ── Register all routers ──────────────────────────────────────────────────────
# Each router handles a specific feature of the app
app.include_router(chat_router)
app.include_router(recommendations_router)
app.include_router(tracker_router)
app.include_router(evaluation_router)

# ── Startup Event ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """
    Runs automatically when the server starts.
    Initializes the database and creates tables if they don't exist.
    """
    print("🚀 InternMitra backend starting up...")
    init_db()
    print("✅ All systems ready!")


# ── Root endpoint ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    """Health check endpoint — confirms the API is running."""
    return {
        "message": "Welcome to InternMitra API 🎓",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check for deployment monitoring."""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_model": os.getenv("MODEL_NAME", "llama3-8b-8192"),
        "environment": os.getenv("APP_ENV", "development")
    }


# ── Run the server ────────────────────────────────────────────────────────────
# This block only runs when you execute: python main.py directly
# ── Run the server ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )