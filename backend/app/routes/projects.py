from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from app.db.database import get_db
from app.schemas.schemas import ProjectResponse, ProjectCreate, ProjectUpdate
from app.services import project_service
from app.utils.cloudinary_utils import upload_image as upload_to_cloudinary

# ✅ router MUST be first
router = APIRouter(prefix="/projects")

# 🔥 IMAGE UPLOAD API (Cloudinary)
@router.post("/upload-image")
def upload_image(file: UploadFile = File(...)):
    cloudinary_url = upload_to_cloudinary(file.file, folder="projects")
    if not cloudinary_url:
        raise HTTPException(status_code=500, detail="Image upload to Cloudinary failed")

    return {
        "image_url": cloudinary_url
    }

# ✅ GET ALL PROJECTS
@router.get("/", response_model=List[ProjectResponse])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return project_service.get_projects(db, skip=skip, limit=limit)

# ✅ GET SINGLE PROJECT
@router.get("/{id}", response_model=ProjectResponse)
def get_project(id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# ✅ CREATE PROJECT
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def add_project(project: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db=db, project=project)

# ✅ UPDATE PROJECT
@router.put("/{id}", response_model=ProjectResponse)
def update_project(id: str, project: ProjectUpdate, db: Session = Depends(get_db)):
    updated_project = project_service.update_project(db=db, project_id=id, project_update=project)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

# ✅ DELETE PROJECT
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(id: str, db: Session = Depends(get_db)):
    success = project_service.delete_project(db=db, project_id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return None
