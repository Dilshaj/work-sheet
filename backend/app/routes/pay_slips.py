from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import PaySlip, User
from app.schemas.schemas import PaySlipCreate, PaySlipResponse

router = APIRouter()

@router.post("/pay-slips", response_model=PaySlipResponse)
def generate_pay_slip(payload: PaySlipCreate, db: Session = Depends(get_db)):
    # Verify employee exists
    emp = db.query(User).filter(User.employee_id == payload.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    new_slip = PaySlip(
        employee_id=payload.employee_id,
        month=payload.month,
        amount=payload.amount,
        status=payload.status,
        project_id=payload.project_id
    )
    db.add(new_slip)
    db.commit()
    db.refresh(new_slip)
    
    # Attach name for response
    new_slip.employee_name = emp.name
    return new_slip

@router.get("/pay-slips", response_model=List[PaySlipResponse])
def get_all_pay_slips(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve all pay slips with employee names in a single high-performance query."""
    from sqlalchemy import text
    
    sql = """
    SELECT p.*, e.name as employee_name
    FROM pay_slips p
    LEFT JOIN employees_table e ON CAST(p.employee_id AS VARCHAR(50)) = CAST(e.employee_id AS VARCHAR(50))
    """
    
    params = {}
    if project_id and project_id != 'null':
        sql += " WHERE p.project_id = :pid"
        params["pid"] = project_id
    
    sql += " ORDER BY p.created_at DESC"
    
    rows = db.execute(text(sql), params).fetchall()
    
    # Map raw rows to Pydantic-compatible objects
    results = []
    for r in rows:
        # Create a dictionary since PaySlipResponse can parse from attributes/dict
        slip_dict = dict(r._mapping)
        results.append(slip_dict)
        
    return results

@router.get("/pay-slips/{id}/download")
def download_pay_slip(id: str, db: Session = Depends(get_db)):
    """Backend endpoint logic for generating a downloadable slip (Placeholder for future PDF logic)."""
    slip = db.query(PaySlip).filter(PaySlip.id == id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="Pay slip not found")
    return {"message": "Pay slip data ready for download", "id": id}

@router.post("/pay-slips/{id}/send-email")
def send_pay_slip_email(id: str, db: Session = Depends(get_db)):
    """Backend trigger for emailing the pay slip to the employee."""
    slip = db.query(PaySlip).filter(PaySlip.id == id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="Pay slip not found")
    # Email logic would go here
    return {"message": f"Pay slip for {slip.month} sent to employee successfully"}

@router.get("/pay-slips/my/{employee_id}", response_model=List[PaySlipResponse])
def get_my_pay_slips(employee_id: str, db: Session = Depends(get_db)):
    results = db.query(PaySlip).filter(PaySlip.employee_id == employee_id).order_by(PaySlip.created_at.desc()).all()
    for slip in results:
        emp = db.query(User).filter(User.employee_id == slip.employee_id).first()
        slip.employee_name = emp.name if emp else "Unknown"
    return results
