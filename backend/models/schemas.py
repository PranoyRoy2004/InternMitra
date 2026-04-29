# schemas.py - Defines the shape of data going in and out of the API
# Pydantic automatically validates all incoming requests

from pydantic import BaseModel
from typing import Optional, List

# ── Chat ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str          # Unique ID per user session
    message: str             # User's message
    user_id: Optional[str] = "guest"

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    sources: Optional[List[str]] = []   # RAG sources used

# ── Recommendations ───────────────────────────────────
class RecommendRequest(BaseModel):
    skills: List[str]                   # e.g. ["Python", "ML"]
    interests: str                      # e.g. "AI and data science"
    experience_level: str               # "beginner", "intermediate", "advanced"
    user_id: Optional[str] = "guest"

class InternshipItem(BaseModel):
    role: str
    company_type: str
    skills_required: List[str]
    learning_roadmap: List[str]
    difficulty: str

class RecommendResponse(BaseModel):
    recommendations: List[InternshipItem]
    advice: str

# ── Tracker ───────────────────────────────────────────
class TrackerCreate(BaseModel):
    user_id: str
    company: str
    role: str
    status: Optional[str] = "Applied"
    notes: Optional[str] = ""
    applied_date: Optional[str] = ""

class TrackerUpdate(BaseModel):
    status: str
    notes: Optional[str] = ""

class TrackerItem(BaseModel):
    id: int
    user_id: str
    company: str
    role: str
    status: str
    notes: Optional[str]
    applied_date: Optional[str]
    created_at: str

# ── Evaluation ────────────────────────────────────────
class EvalResponse(BaseModel):
    run_id: str
    total: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    details: List[dict]