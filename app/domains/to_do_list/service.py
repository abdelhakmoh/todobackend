from fastapi import HTTPException
from datetime import datetime, timedelta, date
import uuid
from . import models, schemas

def get_all_tasks(filter_type: str = None, category: int = None):
    filtered_tasks = list(models.tasks_db.values())
    if category is not None:
        filtered_tasks = [t for t in filtered_tasks if t.category == category]
    if filter_type == "completed":
        filtered_tasks = [t for t in filtered_tasks if t.isCompleted]
    elif filter_type == "active":
        filtered_tasks = [t for t in filtered_tasks if not t.isCompleted]
    elif filter_type == "starred":
        filtered_tasks = [t for t in filtered_tasks if t.isStarred]
    return {"tasks": [t.dict() for t in filtered_tasks], "total": len(filtered_tasks)}

def create_task(task: schemas.Task):
    if task.id in models.tasks_db:
        raise HTTPException(status_code=409, detail="TASK_ID_EXISTS")
    models.tasks_db[task.id] = task
    return task.dict()

def toggle_task_completion(task_id: str, is_completed: bool, completed_at: str = None):
    if task_id not in models.tasks_db:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")
        
    task = models.tasks_db[task_id]
    task.isCompleted = is_completed
    task.completedAt = completed_at or (datetime.utcnow().isoformat() + "Z")
    
    recurring_created = False
    gamif = models.gamification_db["default_user"]

    if task.isCompleted:
        today_str = str(date.today())
        gamif.progress += 10
        try:
            last_comp_date = date.fromisoformat(gamif.lastCompleted)
            if last_comp_date == date.today() - timedelta(days=1):
                gamif.streak += 1
            elif last_comp_date < date.today() - timedelta(days=1):
                gamif.streak = 1
        except ValueError:
            gamif.streak = 1
        gamif.lastCompleted = today_str

        if task.recurringType != schemas.RecurringType.NONE and task.dueDate:
            try:
                base_date = datetime.fromisoformat(task.dueDate.replace("Z", "+00:00")).replace(tzinfo=None)
                if task.recurringType == schemas.RecurringType.DAILY:
                    new_date = base_date + timedelta(days=1)
                elif task.recurringType == schemas.RecurringType.WEEKLY:
                    new_date = base_date + timedelta(days=7)
                elif task.recurringType == schemas.RecurringType.MONTHLY:
                    new_date = base_date + timedelta(days=30)

                new_task = task.copy(deep=True)
                new_task.id = str(uuid.uuid4())
                new_task.isCompleted = False
                new_task.completedAt = None
                new_task.dueDate = new_date.isoformat() + "Z"
                models.tasks_db[new_task.id] = new_task
                recurring_created = True
            except ValueError:
                pass 

    return {"task": task.dict(), "gamification": gamif.dict(), "recurringTaskCreated": recurring_created}

def get_stats():
    total = len(models.tasks_db)
    completed = sum(1 for t in models.tasks_db.values() if t.isCompleted)
    active = total - completed
    starred = sum(1 for t in models.tasks_db.values() if t.isStarred)
    today_str = str(date.today())
    overdue = 0
    today_tasks = 0
    tasks_by_cat = {str(i): 0 for i in range(7)}
    tasks_by_pri = {str(i): 0 for i in range(3)}

    for task in models.tasks_db.values():
        tasks_by_cat[str(int(task.category))] += 1
        tasks_by_pri[str(int(task.priority))] += 1
        if task.dueDate and not task.isCompleted:
            task_date = task.dueDate[:10] 
            if task_date < today_str:
                overdue += 1
            elif task_date == today_str:
                today_tasks += 1

    rate = round(completed / total, 2) if total > 0 else 0.0
    return {
        "totalTasks": total, "completedTasks": completed, "activeTasks": active,
        "overdueTasks": overdue, "todayTasks": today_tasks, "starredTasks": starred,
        "completionRate": rate, "tasksByCategory": tasks_by_cat, "tasksByPriority": tasks_by_pri
    }