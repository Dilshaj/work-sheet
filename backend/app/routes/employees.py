from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.schemas.schemas import EmployeeResponse, EmployeeCreate, EmployeeProgressUpdate
from app.services import employee_service

class AssignProjectRequest(BaseModel):
    projectId: Optional[str] = None

router = APIRouter(prefix="/employees")

@router.get("", response_model=List[EmployeeResponse])
def get_employees(skip: int = 0, limit: int = 100, project_id: str = None, db: Session = Depends(get_db)):
    """Retrieve a list of all employees (users) in the system. Optionally filter by project_id."""
    employees = employee_service.get_employees(db, skip=skip, limit=limit, project_id=project_id)
    return employees

@router.get("/search", response_model=EmployeeResponse)
def search_employee(employee_id: str = None, name: str = None, db: Session = Depends(get_db)):
    """Search for an employee by employee_id or name (case-insensitive partial match).
    Used by the Add Employee modal for auto-fill functionality."""
    employee = employee_service.search_employee(db, employee_id=employee_id, name=name)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.get("/{id}", response_model=EmployeeResponse)
def get_employee(id: str, db: Session = Depends(get_db)):
    """Retrieve a specific employee by ID. Used by Employee Profile."""
    employee = employee_service.get_employee(db, user_id=id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

import logging
logger = logging.getLogger(__name__)

@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee with a default password of 'user'. Validates employee_id uniqueness."""
    from app.models.models import User
    
    logger.info(f"Incoming Employee Payload: {employee.model_dump()}")
    
    # Check employee_id uniqueness
    existing = db.query(User).filter(User.employee_id == employee.employee_id).first()
    if existing:
        logger.warning(f"Creation failed: Employee ID {employee.employee_id} already exists")
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    try:
        new_employee = employee_service.create_employee(db=db, employee=employee)
        return new_employee
    except Exception as e:
        # Step 4: Return proper JSON error instead of crashing
        logger.error(f"Route failure in create_employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(e)}"
        )

@router.put("/{id}/progress", response_model=EmployeeResponse)
def update_progress(id: str, progress: EmployeeProgressUpdate, db: Session = Depends(get_db)):
    """Update an employee's daily and weekly progress percentages from sliders."""
    updated_employee = employee_service.update_employee_progress(db=db, user_id=id, progress=progress)
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated_employee

@router.put("/{id}/assign", response_model=EmployeeResponse)
def assign_project(id: str, body: AssignProjectRequest, db: Session = Depends(get_db)):
    """Assign an existing employee to a project (or remove them by passing null projectId)."""
    employee = employee_service.assign_employee_project(db=db, user_id=id, project_id=body.projectId)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(id: str, db: Session = Depends(get_db)):
    """Delete an employee and cascade their tasks/attendance based on SQLAlchemy relations."""
    success = employee_service.delete_employee(db=db, user_id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return None

@router.delete("/admin/delete-employee/{employee_id}")
def delete_employee_admin(employee_id: str, db: Session = Depends(get_db)):
    """Admin endpoint to delete an employee by their business ID."""
    success = employee_service.delete_employee_by_eid(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}
