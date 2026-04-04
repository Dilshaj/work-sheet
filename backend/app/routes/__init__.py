from fastapi import APIRouter
from app.routes import auth, employees, projects, tasks, attendance, dashboard, profile

router = APIRouter()
