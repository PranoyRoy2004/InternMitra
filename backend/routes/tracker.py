# tracker.py - API endpoints for the internship application tracker
# Full CRUD - Create, Read, Update, Delete internship applications

from fastapi import APIRouter, HTTPException
from models.schemas import TrackerCreate, TrackerUpdate, TrackerItem
from models.database import get_connection
from typing import List

router = APIRouter(prefix="/tracker", tags=["Tracker"])


@router.post("/add", response_model=TrackerItem)
async def add_application(request: TrackerCreate):
    """
    Add a new internship application to the tracker.

    Example request body:
    {
        "user_id": "user123",
        "company": "Google",
        "role": "ML Intern",
        "status": "Applied",
        "notes": "Applied via LinkedIn",
        "applied_date": "2024-06-01"
    }
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tracker (user_id, company, role, status, notes, applied_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.user_id,
            request.company,
            request.role,
            request.status,
            request.notes,
            request.applied_date
        ))

        conn.commit()
        new_id = cursor.lastrowid

        # Fetch the newly created record to return it
        cursor.execute("SELECT * FROM tracker WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        conn.close()

        return TrackerItem(**dict(row))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding application: {str(e)}")


@router.get("/list/{user_id}", response_model=List[TrackerItem])
async def list_applications(user_id: str):
    """
    Get all internship applications for a user.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tracker
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [TrackerItem(**dict(row)) for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applications: {str(e)}")


@router.put("/update/{app_id}", response_model=TrackerItem)
async def update_application(app_id: int, request: TrackerUpdate):
    """
    Update the status or notes of an application.

    Example request body:
    {
        "status": "Interview",
        "notes": "Interview scheduled for June 10th"
    }
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tracker
            SET status = ?, notes = ?
            WHERE id = ?
        """, (request.status, request.notes, app_id))

        conn.commit()

        # Return updated record
        cursor.execute("SELECT * FROM tracker WHERE id = ?", (app_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Application not found")

        return TrackerItem(**dict(row))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating application: {str(e)}")


@router.delete("/delete/{app_id}")
async def delete_application(app_id: int):
    """
    Delete an internship application from the tracker.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tracker WHERE id = ?", (app_id,))
        conn.commit()
        conn.close()

        return {"message": f"Application {app_id} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting application: {str(e)}")


@router.get("/stats/{user_id}")
async def get_stats(user_id: str):
    """
    Returns application statistics for a user's dashboard.
    Counts applications by status.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM tracker
            WHERE user_id = ?
            GROUP BY status
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        stats = {row["status"]: row["count"] for row in rows}

        # Ensure all statuses are present even if count is 0
        for status in ["Applied", "Interview", "Rejected", "Offer"]:
            if status not in stats:
                stats[status] = 0

        stats["total"] = sum(stats.values())
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")