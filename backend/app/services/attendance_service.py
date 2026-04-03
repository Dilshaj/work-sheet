from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Attendance, User

def get_current_timestamps():
    """Helper to get current date formatted YYYY-MM-DD and full ISO timestamp."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.isoformat()

def get_all_attendance(db: Session, skip: int = 0, limit: int = 100, project_id: str = None):
    """Retrieve tracking list of all attendance logs, with optional project filtering."""
    from sqlalchemy import text
    if project_id:
        # We join with User to filter attendance logs by project
        # Using CAST for MSSQL performance
        sql = """
        SELECT a.id, a.employee_id, a.date, a.check_in, a.check_out, a.location_name, a.latitude, a.longitude, a.created_at 
        FROM attendance a
        INNER JOIN employees_table u ON CAST(a.employee_id AS VARCHAR(50)) = CAST(u.employee_id AS VARCHAR(50))
        WHERE CAST(u.project_id AS VARCHAR(50)) = :pid
        ORDER BY a.created_at DESC
        """
        rows = db.execute(text(sql), {"pid": project_id}).fetchall()
        # Convert raw rows to Attendance model instances so route can attach userName
        logs = []
        for r in rows:
            obj = Attendance()
            obj.id = r[0]
            obj.employee_id = r[1]
            obj.date = r[2]
            obj.check_in = r[3]
            obj.check_out = r[4]
            obj.location_name = r[5]
            obj.latitude = r[6]
            obj.longitude = r[7]
            obj.created_at = r[8]
            logs.append(obj)
        return logs
    
    # Case: Global retrieval (no project filter)
    sql = """
    SELECT id, employee_id, date, check_in, check_out, location_name, latitude, longitude, created_at 
    FROM attendance
    ORDER BY created_at DESC
    """
    rows = db.execute(text(sql)).fetchall()
    logs = []
    # Limit manually for now
    for r in rows[skip:skip+limit]:
        obj = Attendance()
        obj.id = r[0]
        obj.employee_id = r[1]
        obj.date = r[2]
        obj.check_in = r[3]
        obj.check_out = r[4]
        obj.location_name = r[5]
        obj.latitude = r[6]
        obj.longitude = r[7]
        obj.created_at = r[8]
        logs.append(obj)
    return logs

def get_attendance_by_user(db: Session, identifier: str):
    """Retrieve all attendance logs for a single user by employee ID."""
    return db.query(Attendance).filter(
        Attendance.employee_id == identifier
    ).order_by(Attendance.created_at.desc()).all()

def get_active_checkin(db: Session, identifier: str, current_date: str):
    """Finds if a user is currently checked in bounds of today by employee ID."""
    return db.query(Attendance).filter(
        Attendance.employee_id == identifier,
        Attendance.date == current_date,
        Attendance.check_out == None
    ).first()

def check_in(db: Session, user_id: str, employee_id: str = None, project_id: str = None, latitude: float = None, longitude: float = None, location_name: str = None):
    """Logs a user as checked in, capturing GPS location and area name if provided."""
    current_date, current_time = get_current_timestamps()
    
    # Use employee_id as primary identifier now
    identifier = employee_id or user_id

    # Prevent duplicate active checkins
    existing = get_active_checkin(db, identifier, current_date)
    if existing:
        return existing, False 

    db_attendance = Attendance(
        employee_id=identifier,
        date=current_date,
        check_in=current_time,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    
    return db_attendance, True

def check_out(db: Session, log_id: str):
    """Closes an active check-in log setting the check-out timestamp."""
    _, current_time = get_current_timestamps()
    
    db_attendance = db.query(Attendance).filter(Attendance.id == log_id).first()
    if db_attendance and not db_attendance.check_out:
        db_attendance.check_out = current_time
        db.commit()
        db.refresh(db_attendance)
        return db_attendance
    return None

def export_attendance_to_excel(db: Session):
    """Fetches all attendance records and converts them to an Excel file using pandas."""
    import pandas as pd
    from io import BytesIO
    
    logs = get_all_attendance(db, limit=2000) # Fetch a reasonable amount for export
    
    data = []
    for log in logs:
        # Get user name for better report
        user = db.query(User).filter(User.employee_id == log.employee_id).first()
        user_name = user.name if user else "Unknown"
        
        data.append({
            "Employee Name": user_name,
            "Employee ID": log.employee_id,
            "Date": log.date,
            "Check-In Time": log.check_in.split('T')[1][:5] if log.check_in else "N/A",
            "Check-Out Time": log.check_out.split('T')[1][:5] if log.check_out else "N/A"
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    
    output.seek(0)
    return output
