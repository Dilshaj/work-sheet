from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse
from app.routes.auth import get_current_user
from app.utils.cloudinary_utils import upload_image as upload_to_cloudinary

router = APIRouter(prefix="/employee")

@router.get("/profile/{user_id}", response_model=UserResponse)
def get_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/update-profile")
@router.put("/employee/update-profile") # Supporting the specific naming requested
async def update_profile(
    name: str = Form(...),
    email: str = Form(...),
    joining_date: str = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    user.name = name
    user.email = email
    
    # Validation: Joining date cannot be future date
    from datetime import datetime
    if joining_date:
        try:
            join_date_obj = datetime.strptime(joining_date, '%Y-%m-%d')
            if join_date_obj > datetime.now():
                raise HTTPException(status_code=400, detail="Joining date cannot be in the future.")
            user.joining_date = joining_date
        except ValueError:
            pass 

    if profile_image:
        # Upload to Cloudinary instead of saving locally
        cloudinary_url = upload_to_cloudinary(profile_image.file, folder="avatars")
        if not cloudinary_url:
             raise HTTPException(status_code=500, detail="Image upload to Cloudinary failed")
        
        user.avatar = cloudinary_url

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
    
    return {
        "message": "Profile updated successfully",
        "user": user
    }
