from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.schemas.schemas import DashboardMetricsResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard")

# Local Schema uniquely serving the User overview 
class UserDashboardMetricsResponse(BaseModel):
    totalTasks: int
    completedTasks: int
    pendingTasks: int

@router.get("/admin", response_model=DashboardMetricsResponse)
def get_admin_metrics(project_id: str = None, db: Session = Depends(get_db)):
    """
    Provides aggregated metrics for the Admin Dashboard.
    If project_id is provided, filters stats specifically for that project.
    """
    metrics = dashboard_service.get_admin_dashboard_metrics(db, project_id=project_id)
    return metrics

@router.get("/employee/{user_id}", response_model=UserDashboardMetricsResponse)
def get_user_metrics(user_id: str, db: Session = Depends(get_db)):
    """
    Provides aggregated, SQL-optimized task split mappings (Pending vs Completed) 
    designed specifically for the individual User Dashboard perspective.
    """
    metrics = dashboard_service.get_user_dashboard_metrics(db, user_id=user_id)
    return metrics
