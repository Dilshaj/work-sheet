from sqlalchemy.orm import Session
from app.models.models import Task, User, Project
from app.schemas.schemas import TaskCreate, TaskStatusUpdate

def get_tasks(db: Session, skip: int = 0, limit: int = 100, project_id: str = None):
    from sqlalchemy import text
    if project_id:
        sql = "SELECT * FROM tasks WHERE CAST(project_id AS VARCHAR(50)) = :pid ORDER BY created_at DESC"
        res = db.execute(text(sql), {"pid": project_id}).fetchall()
        return res
    
    # Generic retrieval with ORDER BY optimization
    sql = "SELECT * FROM tasks ORDER BY created_at DESC"
    res = db.execute(text(sql)).fetchall()
    return res[skip:skip+limit]

def get_task(db: Session, task_id: str):
    from sqlalchemy import text
    sql = "SELECT * FROM tasks WHERE CAST(id AS VARCHAR(50)) = :tid"
    res = db.execute(text(sql), {"tid": task_id}).fetchone()
    return res

def get_tasks_by_employee(db: Session, employee_id: str):
    from sqlalchemy import text
    # assigned_to is a UUID string in the DB, employee_id is also passed as UUID from frontend usually.
    sql = "SELECT * FROM tasks WHERE CAST(assigned_to AS VARCHAR(50)) = :eid"
    res = db.execute(text(sql), {"eid": employee_id}).fetchall()
    return res

def create_task(db: Session, task: TaskCreate):
    # Map from Schema to Model (assignedTo -> assigned_to, projectId -> project_id)
    try:
        print(f"DEBUG: Attempting to insert task '{task.title}' into RDS")
        db_task = Task(
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            priority=task.priority,
            timeline=task.timeline,
            assigned_to=task.assignedTo,
            project_id=task.projectId,
            status="Pending" # Default status on creation per frontend logic
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        print(f"DEBUG: Task '{task.title}' successfully committed tracking to project {task.projectId}")
        return db_task
    except Exception as e:
        db.rollback()
        print(f"DEBUG ERROR: Task creation failed: {e}")
        import logging
        logging.getLogger(__name__).error(f"Task insertion error: {str(e)}")
        raise e

def update_task_status(db: Session, task_id: str, status_update: TaskStatusUpdate):
    db_task = get_task(db, task_id)
    if db_task:
        db_task.status = status_update.status
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: str):
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False
