from sqlalchemy.orm import Session
from app.models.models import User
from app.utils.security import verify_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_employee_id(db: Session, employee_id: str):
    return db.query(User).filter(User.employee_id == employee_id).first()

import logging
logger = logging.getLogger(__name__)

def authenticate_user(db: Session, email: str = None, employee_id: str = None, password: str = None):
    # Retrieve user from the database
    if employee_id:
        user = get_user_by_employee_id(db, employee_id)
    elif email:
        user = get_user_by_email(db, email)
    else:
        return False

    if not user:
        return False
    
    # Properly verify hashed password stored in Database
    if not password:
        return False
        
    if not verify_password(password, user.password_hash):
        return False
        
    return user
