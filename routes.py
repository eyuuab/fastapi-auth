from fastapi import APIRouter, HTTPException, Depends
from models import Task
from auth import get_current_user

router = APIRouter()

tasks = {}

# Create Task 
@router.post("/tasks/")
def create_task(task_id: int, task: Task, user: str = Depends(get_current_user)):
    if task_id in tasks:
        raise HTTPException(status_code=400, detail="Task ID already exists")
    tasks[task_id] = task
    return {"message": f"Task created by {user}", "task": task}

# Get All Tasks 
@router.get("/tasks/")
def get_tasks(user: str = Depends(get_current_user)):
    return tasks
