# recommendations.py - API endpoints for internship recommendations
# Takes user profile and returns AI-powered internship suggestions

from fastapi import APIRouter, HTTPException
from models.schemas import RecommendRequest, RecommendResponse
from services.recommendation_service import generate_recommendations

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/get", response_model=RecommendResponse)
async def get_recommendations(request: RecommendRequest):
    """
    Generate personalized internship recommendations.

    Example request body:
    {
        "skills": ["Python", "Machine Learning", "Pandas"],
        "interests": "I love building AI products and data analysis",
        "experience_level": "beginner",
        "user_id": "user123"
    }
    """
    try:
        # Validate experience level
        valid_levels = ["beginner", "intermediate", "advanced"]
        if request.experience_level.lower() not in valid_levels:
            raise HTTPException(
                status_code=400,
                detail=f"experience_level must be one of: {valid_levels}"
            )

        result = generate_recommendations(
            skills=request.skills,
            interests=request.interests,
            experience_level=request.experience_level.lower()
        )

        return RecommendResponse(
            recommendations=result.get("recommendations", []),
            advice=result.get("advice", "")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.get("/internships")
async def list_all_internships():
    """
    Returns all internships from our local dataset.
    Useful for browsing without AI recommendations.
    """
    try:
        from services.rag_service import load_internships
        internships = load_internships()
        return {"total": len(internships), "internships": internships}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading internships: {str(e)}")