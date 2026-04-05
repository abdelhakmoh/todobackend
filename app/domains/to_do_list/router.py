from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Optional
from . import schemas, service, models

router = APIRouter(
    prefix="/todolist",
    tags=["To-Do List"]
)

def verify_token(authorization: str = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return authorization

@router.get("/tasks", dependencies=[Depends(verify_token)])
def get_all_tasks(filter: Optional[str] = None, category: Optional[int] = None):
    data = service.get_all_tasks(filter, category)
    return {"success": True, "data": data}

@router.post("/tasks", status_code=201, dependencies=[Depends(verify_token)])
def create_task(task: schemas.Task):
    data = service.create_task(task)
    return {"success": True, "data": data}

@router.patch("/tasks/{task_id}/complete", dependencies=[Depends(verify_token)])
def toggle_task_completion(task_id: str, payload: dict):
    data = service.toggle_task_completion(
        task_id=task_id, 
        is_completed=payload.get("isCompleted", True),
        completed_at=payload.get("completedAt")
    )
    return {"success": True, "data": data}

@router.delete("/tasks/completed", dependencies=[Depends(verify_token)])
def delete_completed_tasks():
    completed_ids = [tid for tid, t in models.tasks_db.items() if t.isCompleted]
    for tid in completed_ids:
        del models.tasks_db[tid]
    return {"success": True, "message": f"Deleted {len(completed_ids)} tasks", "data": {"deletedCount": len(completed_ids)}}

@router.get("/goals", dependencies=[Depends(verify_token)])
def get_all_goals():
    return {"success": True, "data": {"goals": {str(k): v for k, v in models.goals_db.items()}}}

@router.post("/goals", dependencies=[Depends(verify_token)])
def set_goal(goal: schemas.GoalInput):
    models.goals_db[goal.category] = goal.targetCount
    return {"success": True, "data": {"goals": {str(k): v for k, v in models.goals_db.items()}}}

@router.get("/gamification", dependencies=[Depends(verify_token)])
def get_gamification():
    return {"success": True, "data": models.gamification_db["default_user"].dict()}

@router.get("/stats", dependencies=[Depends(verify_token)])
def get_stats():
    data = service.get_stats()
    return {"success": True, "data": data}