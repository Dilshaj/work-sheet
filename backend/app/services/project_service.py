from sqlalchemy.orm import Session
from app.models.models import Project
from app.schemas.schemas import ProjectCreate, ProjectUpdate

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve all projects."""
    return db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
def get_project(db: Session, project_id: str):
    """Retrieve a single project by ID."""
    return db.query(Project).filter(Project.id == project_id).first()

def create_project(db: Session, project: ProjectCreate):
    # 🔍 check duplicate
    existing = db.query(Project).filter(Project.name == project.name).first()
    if existing:
        raise Exception("Project already exists")

    db_project = Project(
        name=project.name,
        image=project.image
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project

def update_project(db: Session, project_id: str, project_update: ProjectUpdate):
    """Update an existing project."""
    db_project = get_project(db, project_id)
    if db_project:
        if project_update.name is not None:
            db_project.name = project_update.name
        if project_update.image is not None:
            db_project.image = project_update.image
            
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str):
    """Delete a project. This cascades and nullifies dependencies based on the DB model setup."""
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False
