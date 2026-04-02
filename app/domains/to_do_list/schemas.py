from pydantic import BaseModel, Field
from typing import List, Optional
from enum import IntEnum
import uuid
from datetime import datetime

class TaskPriority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class TaskCategory(IntEnum):
    STUDY = 0
    ASSIGNMENT = 1
    EXAM = 2
    PROJECT = 3
    PERSONAL = 4
    READING = 5
    OTHER = 6

class RecurringType(IntEnum):
    NONE = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3

class SubTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    isCompleted: bool = False

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    isCompleted: bool = False
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory = TaskCategory.STUDY
    dueDate: Optional[str] = None
    dueTimeHour: Optional[int] = Field(None, ge=0, le=23)
    dueTimeMinute: Optional[int] = Field(None, ge=0, le=59)
    remindBeforeMinutes: int = 30
    subTasks: List[SubTask] = []
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    completedAt: Optional[str] = None
    isStarred: bool = False
    recurringType: RecurringType = RecurringType.NONE

class GoalInput(BaseModel):
    category: TaskCategory
    targetCount: int

class Gamification(BaseModel):
    streak: int
    progress: int
    lastCompleted: str