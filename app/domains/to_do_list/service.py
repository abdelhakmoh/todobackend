from sqlalchemy.orm import Session
from . import models, schemas
import uuid
from datetime import datetime

# --- TASKS ---
def get_tasks(db: Session):
    return db.query(models.Task).all()

def get_task_by_id(db: Session, task_id: str):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task: schemas.TaskCreate):
    task_id = task.id if task.id else str(uuid.uuid4())
    db_task = models.Task(
        id=task_id,
        title=task.title,
        description=task.description,
        isCompleted=task.isCompleted,
        priority=task.priority,
        category=task.category,
        dueDate=task.dueDate,
        dueTimeHour=task.dueTimeHour,
        dueTimeMinute=task.dueTimeMinute,
        remindBeforeMinutes=task.remindBeforeMinutes,
        createdAt=datetime.utcnow().isoformat() + "Z",
        isStarred=task.isStarred,
        recurringType=task.recurringType
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Handle Subtasks
    if task.subTasks:
        for st in task.subTasks:
            db_subtask = models.SubTask(id=st.id, title=st.title, isCompleted=st.isCompleted, task_id=task_id)
            db.add(db_subtask)
        db.commit()
        db.refresh(db_task)
    return db_task

def update_task_fully(db: Session, task_id: str, task_update: schemas.TaskCreate):
    db_task = get_task_by_id(db, task_id)
    if not db_task: return None
    
    update_data = task_update.dict(exclude_unset=True, exclude={"subTasks"})
    for key, value in update_data.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def toggle_task_completion(db: Session, task_id: str, is_completed: bool, completed_at: str):
    db_task = get_task_by_id(db, task_id)
    if not db_task: return None
    db_task.isCompleted = is_completed
    db_task.completedAt = completed_at if is_completed else None
    db.commit()
    db.refresh(db_task)
    return db_task

def toggle_star(db: Session, task_id: str, is_starred: bool):
    db_task = get_task_by_id(db, task_id)
    if not db_task: return None
    db_task.isStarred = is_starred
    db.commit()
    db.refresh(db_task)
    return db_task

def toggle_subtask(db: Session, task_id: str, subtask_id: str, is_completed: bool):
    db_subtask = db.query(models.SubTask).filter(models.SubTask.id == subtask_id, models.SubTask.task_id == task_id).first()
    if not db_subtask: return None
    db_subtask.isCompleted = is_completed
    db.commit()
    return get_task_by_id(db, task_id)

def delete_task(db: Session, task_id: str):
    db_task = get_task_by_id(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def delete_completed_tasks(db: Session):
    tasks = db.query(models.Task).filter(models.Task.isCompleted == True).all()
    count = len(tasks)
    for task in tasks:
        db.delete(task)
    db.commit()
    return count

# --- GOALS ---
def get_goals(db: Session):
    goals = db.query(models.WeeklyGoal).all()
    return {str(g.category): g.targetCount for g in goals}

def set_goal(db: Session, goal: schemas.GoalCreate):
    db_goal = db.query(models.WeeklyGoal).filter(models.WeeklyGoal.category == goal.category).first()
    if db_goal:
        db_goal.targetCount = goal.targetCount
    else:
        db_goal = models.WeeklyGoal(category=goal.category, targetCount=goal.targetCount)
        db.add(db_goal)
    db.commit()
    return get_goals(db)

def delete_goal(db: Session, category: int):
    db_goal = db.query(models.WeeklyGoal).filter(models.WeeklyGoal.category == category).first()
    if db_goal:
        db.delete(db_goal)
        db.commit()

# --- GAMIFICATION ---
def get_gamification(db: Session):
    gami = db.query(models.Gamification).first()
    if not gami:
        gami = models.Gamification(streak=0, progress=0)
        db.add(gami)
        db.commit()
        db.refresh(gami)
    return gami

def update_gamification(db: Session, gami_update: schemas.GamificationUpdate):
    gami = get_gamification(db)
    gami.streak = gami_update.streak
    gami.progress = gami_update.progress
    gami.lastCompleted = gami_update.lastCompleted
    db.commit()
    db.refresh(gami)
    return gami

# --- STATS ---
def get_stats(db: Session):
    tasks = db.query(models.Task).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.isCompleted)
    return {
        "totalTasks": total,
        "completedTasks": completed,
        "activeTasks": total - completed,
        "overdueTasks": 0, # Simplify for now
        "todayTasks": 0,
        "starredTasks": sum(1 for t in tasks if t.isStarred),
        "completionRate": round(completed / total, 2) if total > 0 else 0,
        "tasksByCategory": {},
        "tasksByPriority": {}
    }