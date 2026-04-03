import logging
from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.schemas import EmployeeCreate, EmployeeProgressUpdate
from app.utils.security import get_password_hash

logger = logging.getLogger(__name__)

def get_employees(db: Session, skip: int = 0, limit: int = 100, project_id: str = None):
    from sqlalchemy import text
    query = db.query(User).filter(User.role != "admin")
    if project_id:
        # Use CAST to VARCHAR(50) for performance on MSSQL
        query = query.filter(User.project_id == text(f"CAST('{project_id}' AS VARCHAR(50))"))
    return query.order_by(User.created_at).offset(skip).limit(limit).all()

def get_employee(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def search_employee(db: Session, employee_id: str = None, name: str = None):
    """Search by employee_id (exact) or name (case-insensitive contains). Non-admin only."""
    query = db.query(User).filter(User.role != "admin")
    if employee_id:
        return query.filter(User.employee_id == employee_id).first()
    if name:
        return query.filter(User.name.ilike(f"%{name}%")).first()
    return None

def create_employee(db: Session, employee: EmployeeCreate):
    """
    Creates a new employee record.
    TARGET TABLE: employees_table (only source of truth)
    """
    try:
        # STEP 4: Debug Log - Table Name
        print(f"DEBUG: Preparing dynamic insert into table: {User.__tablename__}")
        
        # STEP 4: Debug Log - ID before insert
        print(f"DEBUG: Inserting Employee ID: {employee.employee_id}")

        # Default setup for new employees
        db_user = User(
            employee_id=employee.employee_id,
            name=employee.name,
            email=f"{employee.employee_id.lower()}@eduprova.com",
            role=employee.role or "user",
            password_hash=get_password_hash("user"),
            is_first_login=True,
            project_id=employee.project_id
        )
        
        # STEP 7: Verify SQLAlchemy insert statement
        db.add(db_user)
        logger.info(f"Adding employee {employee.employee_id} to database session")
        
        # STEP 8: Ensure commit() is called
        db.commit()
        
        # STEP 4: Debug Log - Success
        print(f"DEBUG: Successfully committed {employee.employee_id} to {User.__tablename__}")
        
        db.refresh(db_user)
        return db_user
    except Exception as e:
        # Step 3: Rollback on failure
        db.rollback()
        # Step 2: Log exact exception
        error_msg = f"Critical failure during employee creation for {employee.employee_id}: {str(e)}"
        logger.error(error_msg)
        print(f"DEBUG ERROR: {error_msg}")
        # Step 4: Raise to be caught by FastAPI and returned as JSON error (handled by routes)
        raise e

def update_employee_progress(db: Session, user_id: str, progress: EmployeeProgressUpdate):
    try:
        db_user = get_employee(db, user_id)
        if db_user:
            db_user.daily_progress = progress.dailyProgress
            db_user.weekly_progress = progress.weeklyProgress
            db.commit()
            db.refresh(db_user)
            logger.info(f"Updated progress for user {user_id}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update progress for user {user_id}: {str(e)}")
        raise e

def assign_employee_project(db: Session, user_id: str, project_id: str):
    """Assign (or reassign) an existing employee to a project by updating project_id."""
    try:
        from sqlalchemy import text
        db_user = get_employee(db, user_id)
        if db_user:
            # We use direct assignment for simple updates, but for searches we used CAST
            db_user.project_id = project_id
            db.commit()
            db.refresh(db_user)
            logger.info(f"Assigned user {user_id} to project {project_id}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to assign project {project_id} to user {user_id}: {str(e)}")
        raise e

def delete_employee(db: Session, user_id: str):
    try:
        db_user = get_employee(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
            logger.info(f"Deleted user {user_id}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete user {user_id}: {str(e)}")
        raise e

def delete_employee_by_eid(db: Session, employee_id: str):
    """Deletes an employee (user) using their business employee_id. Safety: cannot delete admins."""
    try:
        db_user = db.query(User).filter(User.employee_id == employee_id, User.role != "admin").first()
        if db_user:
            db_user_id = db_user.id
            db.delete(db_user)
            db.commit()
            logger.info(f"Deleted user with employee_id {employee_id} (internal id: {db_user_id})")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete employee {employee_id}: {str(e)}")
        raise e
