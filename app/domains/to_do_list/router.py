from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Optional
from . import schemas, service, models

router = APIRouter(
    prefix="/todolist",
    tags=["To-Do List"]
)

# ─── Auth ─────────────────────────────────────────────────────
def verify_token(authorization: str = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return authorization


# ══════════════════════════════════════════════════════════════
# TASKS
# ══════════════════════════════════════════════════════════════

# ─── Get All Tasks ────────────────────────────────────────────
@router.get("/tasks", dependencies=[Depends(verify_token)])
def get_all_tasks(filter: Optional[str] = None, category: Optional[int] = None):
    data = service.get_all_tasks(filter, category)
    return {"success": True, "data": data}


# ─── Create Task ──────────────────────────────────────────────
@router.post("/tasks", status_code=201, dependencies=[Depends(verify_token)])
def create_task(task: schemas.Task):
    data = service.create_task(task)
    return {"success": True, "data": data}


# ─── Get Single Task ──────────────────────────────────────────
@router.get("/tasks/{task_id}", dependencies=[Depends(verify_token)])
def get_task(task_id: str):
    if task_id not in models.tasks_db:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")
    return {"success": True, "data": models.tasks_db[task_id].dict()}


# ─── Update Task ──────────────────────────────────────────────
@router.put("/tasks/{task_id}", dependencies=[Depends(verify_token)])
def update_task(task_id: str, task: schemas.Task):
    if task_id not in models.tasks_db:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")
    models.tasks_db[task_id] = task
    return {"success": True, "data": task.dict()}


# ─── Toggle Task Completion ───────────────────────────────────
@router.patch("/tasks/{task_id}/complete", dependencies=[Depends(verify_token)])
def toggle_task_completion(task_id: str, payload: dict):
    data = service.toggle_task_completion(
        task_id=task_id,
        is_completed=payload.get("isCompleted", True),
        completed_at=payload.get("completedAt")
    )
    return {"success": True, "data": data}


# ─── Toggle Star ──────────────────────────────────────────────
@router.patch("/tasks/{task_id}/star", dependencies=[Depends(verify_token)])
def toggle_star(task_id: str, payload: dict):
    if task_id not in models.tasks_db:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")
    models.tasks_db[task_id].isStarred = payload.get("isStarred", False)
    return {"success": True, "data": models.tasks_db[task_id].dict()}


# ─── Toggle SubTask Completion ────────────────────────────────
@router.patch("/tasks/{task_id}/subtasks/{sub_id}", dependencies=[Depends(verify_token)])
def toggle_subtask(task_id: str, sub_id: str, payload: dict):
    if task_id not in models.tasks_db:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")
    task = models.tasks_db[task_id]
    subtask_found = False
    for subtask in task.subTasks:
        if subtask.id == sub_id:
            subtask.isCompleted = payload.get("isCompleted", False)
            subtask_found = True
            break
    if not subtask_found:
        raise HTTPException(status_code=404, detail="SUBTASK_NOT_FOUND")
    return {"success": True, "data": task.dict()}


# ─── Delete Task ──────────────────────────────────────────────
@router.delete("/tasks/{task_id}", dependencies=[Depends(verify_token)])
def delete_task(task_id: str):
    if task_id not in models.tasks_db:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")
    del models.tasks_db[task_id]
    return {"success": True, "message": "Task deleted successfully"}
# ─── Delete All Completed Tasks ───────────────────────────────
@router.delete("/tasks/completed", dependencies=[Depends(verify_token)])
def delete_completed_tasks():
    completed_ids = [tid for tid, t in models.tasks_db.items() if t.isCompleted]
    for tid in completed_ids:
        del models.tasks_db[tid]
    return {
        "success": True,
        "message": f"Deleted {len(completed_ids)} completed tasks",
        "data": {"deletedCount": len(completed_ids)}
    }


# ══════════════════════════════════════════════════════════════
# GOALS
# ══════════════════════════════════════════════════════════════

# ─── Get All Goals ────────────────────────────────────────────
@router.get("/goals", dependencies=[Depends(verify_token)])
def get_all_goals():
    return {"success": True, "data": {"goals": {str(k): v for k, v in models.goals_db.items()}}}


# ─── Set / Update Goal ────────────────────────────────────────
@router.post("/goals", dependencies=[Depends(verify_token)])
def set_goal(goal: schemas.GoalInput):
    models.goals_db[goal.category] = goal.targetCount
    return {"success": True, "data": {"goals": {str(k): v for k, v in models.goals_db.items()}}}


# ─── Delete Goal ──────────────────────────────────────────────
@router.delete("/goals/{category}", dependencies=[Depends(verify_token)])
def delete_goal(category: int):
    if category not in models.goals_db:
        raise HTTPException(status_code=404, detail="GOAL_NOT_FOUND")
    del models.goals_db[category]
    return {"success": True, "message": "Goal removed"}


# ══════════════════════════════════════════════════════════════
# GAMIFICATION
# ══════════════════════════════════════════════════════════════

# ─── Get Gamification ─────────────────────────────────────────
@router.get("/gamification", dependencies=[Depends(verify_token)])
def get_gamification():
    return {"success": True, "data": models.gamification_db["default_user"].dict()}


# ─── Update Gamification ──────────────────────────────────────
@router.put("/gamification", dependencies=[Depends(verify_token)])
def update_gamification(payload: schemas.Gamification):
    models.gamification_db["default_user"].streak = payload.streak
    models.gamification_db["default_user"].progress = payload.progress
    models.gamification_db["default_user"].lastCompleted = payload.lastCompleted
    return {"success": True, "data": models.gamification_db["default_user"].dict()}


# ══════════════════════════════════════════════════════════════
# STATS
# ══════════════════════════════════════════════════════════════

# ─── Get Stats ────────────────────────────────────────────────
@router.get("/stats", dependencies=[Depends(verify_token)])
def get_stats():
    data = service.get_stats()
    return {"success": True, "data": data}