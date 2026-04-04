from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import LeaveRequest, User
from app.schemas.schemas import LeaveRequestCreate, LeaveRequestResponse
router = APIRouter(prefix="/employee")

def attach_user_name(db: Session, leave_log):
    """Utility function to append employee name using optimized SQL."""
    from sqlalchemy import text
    sql = "SELECT name FROM employees_table WHERE CAST(employee_id AS VARCHAR(50)) = :eid"
    res = db.execute(text(sql), {"eid": leave_log.employee_id}).fetchone()
    setattr(leave_log, "userName", res[0] if res else "Unknown User")
    return leave_log

@router.post("/apply-leave", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def apply_leave(leave_data: LeaveRequestCreate, db: Session = Depends(get_db)):
    try:
        new_leave = LeaveRequest(
            employee_id=leave_data.employee_id,
            leave_type=leave_data.leave_type,
            from_date=leave_data.from_date,
            to_date=leave_data.to_date,
            reason=leave_data.reason,
            status="Pending"
        )
        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)
        return attach_user_name(db, new_leave)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit leave: {str(e)}")

@router.get("/my-leaves/{employee_id}", response_model=List[LeaveRequestResponse])
def get_user_leaves(employee_id: str, db: Session = Depends(get_db)):
    from sqlalchemy import text
    sql = """
    SELECT id, employee_id, leave_type, from_date, to_date, reason, status, created_at 
    FROM leave_requests 
    WHERE CAST(employee_id AS VARCHAR(50)) = :eid
    ORDER BY created_at DESC
    """
    rows = db.execute(text(sql), {"eid": employee_id}).fetchall()
    leaves = []
    for r in rows:
        obj = LeaveRequest()
        obj.id = r[0]
        obj.employee_id = r[1]
        obj.leave_type = r[2]
        obj.from_date = r[3]
        obj.to_date = r[4]
        obj.reason = r[5]
        obj.status = r[6]
        obj.created_at = r[7]
        leaves.append(attach_user_name(db, obj))
    return leaves

@router.get("/all-leaves", response_model=List[LeaveRequestResponse])
def get_all_leaves(db: Session = Depends(get_db)):
    from sqlalchemy import text
    # Optimized raw SQL list for MSSQL driver stability
    sql = """
    SELECT id, employee_id, leave_type, from_date, to_date, reason, status, created_at 
    FROM leave_requests 
    ORDER BY created_at DESC
    """
    rows = db.execute(text(sql)).fetchall()
    leaves = []
    for r in rows:
        obj = LeaveRequest()
        obj.id = r[0]
        obj.employee_id = r[1]
        obj.leave_type = r[2]
        obj.from_date = r[3]
        obj.to_date = r[4]
        obj.reason = r[5]
        obj.status = r[6]
        obj.created_at = r[7]
        leaves.append(attach_user_name(db, obj))
    return leaves

@router.patch("/update-status/{leave_id}", response_model=LeaveRequestResponse)
def update_leave_status(leave_id: str, status: str, db: Session = Depends(get_db)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = status
    db.commit()
    db.refresh(leave)
    return attach_user_name(db, leave)
