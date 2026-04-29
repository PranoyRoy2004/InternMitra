# evaluation.py - API endpoint to trigger AI evaluation pipeline
# Runs the evaluation suite and returns metrics

from fastapi import APIRouter, HTTPException
from models.schemas import EvalResponse

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.post("/run", response_model=EvalResponse)
async def run_evaluation():
    """
    Triggers the full AI evaluation pipeline.
    Runs all test questions, compares with expected answers,
    and returns Accuracy, Precision, Recall, F1 Score.
    """
    try:
        from evaluation.run_eval import run_full_evaluation
        result = await run_full_evaluation()
        return EvalResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")


@router.get("/history")
async def get_eval_history():
    """
    Returns past evaluation run results from the database.
    Useful for tracking AI improvement over time.
    """
    try:
        from models.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT run_id, question, expected, got, score, created_at
            FROM eval_logs
            ORDER BY created_at DESC
            LIMIT 50
        """)

        rows = cursor.fetchall()
        conn.close()

        return {"history": [dict(row) for row in rows]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History error: {str(e)}")