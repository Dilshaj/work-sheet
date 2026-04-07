import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
# v1.1.0-deploy
import os

from app.core.config import settings
from app.db.database import get_db, test_database_connection, engine, Base
from app.routes import auth, employees, projects, tasks, attendance, dashboard, profile, offer_letter, employee_leaves, pay_slips

# 🔹 Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 🔥 FIXED LIFESPAN
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Database...")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified.")

        from app.db.database import SessionLocal
        from app.models.models import User
        from app.utils.security import get_password_hash

        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.role == "admin").first()

            if admin_user:
                logger.info("Admin user already exists. Skipping setup.")
            else:
                logger.info("Creating default admin user...")
                new_admin = User(
                    name="Admin",
                    employee_id="ADMIN-001",
                    email="dilshajceo@dilshajinfotech.tech",
                    password_hash=get_password_hash("admin@123"),
                    role="admin",
                    is_first_login=False
                )
                db.add(new_admin)
                db.commit()
                logger.info("Default admin user created.")

        except Exception as e:
            logger.error(f"Admin setup error: {e}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error executing schema verification: {e}")

    yield
    logger.info("Shutting down API Service...")


# 🔥 APP INIT
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# 🔹 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Static
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 🔹 Routes
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(employees.router, prefix="/api", tags=["Employees"])
app.include_router(projects.router, prefix="/api", tags=["Projects"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(offer_letter.router, prefix="/api", tags=["Offer Letter"])
app.include_router(employee_leaves.router, prefix="/api", tags=["Leaves"])
app.include_router(pay_slips.router, prefix="/api", tags=["Pay Slips"])

# 🔹 Serve React Frontend (Single Repo Deployment)
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "work-updates", "dist")

if os.path.exists(FRONTEND_PATH):
    # Serve assets folder specifically
    assets_path = os.path.join(FRONTEND_PATH, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    # Add a catch-all route for SPA routing (this must be the LAST route)
    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # 1. Skip API/Static/Uploads entirely so they fall through to their respective routers/mounts
        if any(full_path.startswith(p) for p in ["api", "static", "uploads", "assets"]):
            raise HTTPException(status_code=404, detail="Not Found")
        
        # 2. Check if it's a specific file (like favicon.ico or vite.svg)
        file_path = os.path.join(FRONTEND_PATH, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # 3. Fallback to index.html for React SPA
        return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))
    
    logger.info(f"React production build serving from {FRONTEND_PATH}")
else:
    logger.warning(f"Production dist folder not found at {FRONTEND_PATH}. Serving in API-only mode.")

# 🔹 Health
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

# 🔹 DB Health
@app.get("/api/health/db")
def health_check_db(db: Session = Depends(get_db)):
    if test_database_connection():
        return {"status": "db connected"}
    raise HTTPException(status_code=500, detail="DB failed")
