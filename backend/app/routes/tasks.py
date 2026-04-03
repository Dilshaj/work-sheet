from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.schemas import TaskResponse, TaskCreate, TaskStatusUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks")

@router.get("/", response_model=List[TaskResponse])
def get_all_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all tasks. Can be used for admin dashboard overviews."""
    return task_service.get_tasks(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=TaskResponse)
def get_task(id: str, db: Session = Depends(get_db)):
    """Retrieve a specific task by its ID."""
    task = task_service.get_task(db, task_id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/employee/{user_id}", response_model=List[TaskResponse])
def get_employee_tasks(user_id: str, db: Session = Depends(get_db)):
    """Retrieve all tasks assigned to a specific employee ID."""
    return task_service.get_tasks_by_employee(db, employee_id=user_id)

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task and map it to an employee and project."""
    # Note: Foreign key constraints in the database will automatically reject
    # if the assignedTo user or projectId don't exist in their respective tables.
    try:
        new_task = task_service.create_task(db=db, task=task)
        return new_task
    except Exception as e:
        # Catch FK violations gracefully
        raise HTTPException(status_code=400, detail="Invalid Employee or Project ID mapping.")

@router.put("/{id}/status", response_model=TaskResponse)
def update_task_status(id: str, status_update: TaskStatusUpdate, db: Session = Depends(get_db)):
    """Update the status (Pending, In Progress, Completed) of an existing task."""
    updated_task = task_service.update_task_status(db=db, task_id=id, status_update=status_update)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: str, db: Session = Depends(get_db)):
    """Permanently remove a task."""
    success = task_service.delete_task(db=db, task_id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
