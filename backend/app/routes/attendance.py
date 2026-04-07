from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.schemas import AttendanceResponse, CheckInRequest
from app.services import attendance_service
from app.models.models import User

router = APIRouter(prefix="/attendance")

def attach_user_name(db: Session, attendance_log):
    """
    Utility function to append specific expected userName UI strings.
    """
    from sqlalchemy import text
    sql = "SELECT name FROM employees_table WHERE CAST(employee_id AS VARCHAR(50)) = :eid"
    res = db.execute(text(sql), {"eid": attendance_log.employee_id}).fetchone()
    setattr(attendance_log, "userName", res[0] if res else "Unknown User")
    return attendance_log

@router.get("/", response_model=List[AttendanceResponse])
@router.get("/admin/attendance", response_model=List[AttendanceResponse])
def get_attendance_logs(project_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all attendance records with names in a single optimized pass."""
    return attendance_service.get_all_attendance(db, skip=skip, limit=limit, project_id=project_id)

@router.get("/{employee_id}", response_model=List[AttendanceResponse])
def get_employee_attendance(employee_id: str, db: Session = Depends(get_db)):
    """Retrieve all historical attendance records mapped specifically to a single employee."""
    logs = attendance_service.get_attendance_by_user(db, identifier=employee_id)
    for log in logs:
        attach_user_name(db, log)
    return logs

@router.post("/check-in", response_model=AttendanceResponse)
@router.post("/employee/check-in", response_model=AttendanceResponse)
def employee_check_in(request: CheckInRequest, db: Session = Depends(get_db)):
    """Employee endpoint to check-in. Supports both /check-in and /employee/check-in alias."""
    try:
        if not request.employee_id:
            raise HTTPException(status_code=400, detail="employee_id is required")

        log, is_new = attendance_service.check_in(
            db, 
            user_id="", 
            employee_id=request.employee_id,
            latitude=request.latitude,
            longitude=request.longitude,
            location_name=request.location_name
        )
        if not is_new:
            raise HTTPException(status_code=400, detail="Already checked in.")
        
        return attach_user_name(db, log)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"DEBUG ERROR: Check-in failed: {e}")
        # Return a more descriptive error than the generic 500
        raise HTTPException(status_code=400, detail=f"Check-in failed. Please ensure location services are enabled.")

@router.post("/employee/check-out", response_model=AttendanceResponse)
def employee_check_out(request: CheckInRequest, db: Session = Depends(get_db)):
    """Employee endpoint to check-out. Finds the active session for the user."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    active_log = attendance_service.get_active_checkin(db, identifier=request.employee_id, current_date=today)
    
    if not active_log:
        raise HTTPException(status_code=404, detail="No active check-in session found for today.")
    
    log = attendance_service.check_out(db, log_id=active_log.id)
    return attach_user_name(db, log)

@router.get("/admin/export")
def export_attendance(db: Session = Depends(get_db)):
    """Admin endpoint to export all attendance records to Excel."""
    output = attendance_service.export_attendance_to_excel(db)
    
    headers = {
        'Content-Disposition': 'attachment; filename="attendance_report.xlsx"'
    }
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
