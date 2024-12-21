from fastapi import APIRouter, HTTPException
from models import Task

router = APIRouter()

tasks = {}

#create a Task

@router.post('/tasks/')
def create_task(task_id: int, task: Task):
    if task_id in tasks:
        raise HTTPException(status_code = 400, detail = 'Task ID already exists')
    tasks[task_id] = task
    return {
        'message': 'Task created Successfuly', 'task': task
    }

#get tasks
@router.get('/tasks/')
def get_task():
    return tasks

#get specific task
@router.get('/tasks/{task_id}')
def get_task(task_id:int):
    if task_id not in tasks:
        raise HTTPException(status_code = 404, detail = 'Task Not found')
    return tasks[task_id]

#update a task
@router.put('/tasks/{task_id}')
def update_task(task_id: int, task: Task):
    if task_id not in tasks:
        raise HTTPException(status_code = 404, detail = 'Task Not found')
    tasks[task_id] = task
    return { 
        'message': 'Task updated Successfuly', 'task':task
    }

#Delete a task

@router.delete('/tasks/{task_id}')
def delete_task(task_id:int):
    if task_id not in tasks:
        raise HTTPException(status_code = 404, detail = 'Task Not found')
    del tasks[task_id]
    return {
        'message': 'Task Deleted Successfuly'
    } 

