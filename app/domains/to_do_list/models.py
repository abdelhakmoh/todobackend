from typing import Dict
from .schemas import Task, Gamification

# MOCK DATABASE
tasks_db: Dict[str, Task] = {}
goals_db: Dict[int, int] = {}
gamification_db: Dict[str, Gamification] = {
    "default_user": Gamification(streak=0, progress=0, lastCompleted="2000-01-01")
}