from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.models import Project, Task, User, Attendance

from sqlalchemy import text
from sqlalchemy.orm import Session

def get_admin_dashboard_metrics(db: Session, project_id: str = None):
    """
    Agregated SQL metrics for Admin Dashboard overview using Raw SQL for performance.
    """
    try:
        if project_id:
            # Metrics for a specific project
            sql = text("""
                SELECT 
                    1 as active_projects,
                    (SELECT COUNT(*) FROM employees_table WHERE user_role = 'user' AND project_id = CAST(:pid AS VARCHAR(50))) as active_employees,
                    (SELECT COUNT(*) FROM tasks WHERE project_id = CAST(:pid AS VARCHAR(50))) as total_tasks,
                    (SELECT COUNT(*) FROM tasks WHERE status = 'Completed' AND project_id = CAST(:pid AS VARCHAR(50))) as completed_tasks
            """)
            params = {"pid": str(project_id)}
        else:
            # Global Metrics
            sql = text("""
                SELECT 
                    (SELECT COUNT(*) FROM projects) as active_projects,
                    (SELECT COUNT(*) FROM employees_table WHERE user_role = 'user') as active_employees,
                    (SELECT COUNT(*) FROM tasks) as total_tasks,
                    (SELECT COUNT(*) FROM tasks WHERE status = 'Completed') as completed_tasks
            """)
            params = {}

        # Use con.execute directly for speed
        with db.get_bind().connect() as connection:
            result = connection.execute(sql, params).fetchone()

        if result:
            return {
                "activeProjects": int(result[0] or 0),
                "activeEmployees": int(result[1] or 0),
                "totalTasks": int(result[2] or 0),
                "completedTasks": int(result[3] or 0)
            }
        
        return {
            "activeProjects": 0, "activeEmployees": 0, "totalTasks": 0, "completedTasks": 0
        }
    except Exception as e:
        print(f"CRITICAL Error calculating dashboard metrics: {e}")
        return {
            "activeProjects": 0, "activeEmployees": 0, "totalTasks": 0, "completedTasks": 0
        }

def get_user_dashboard_metrics(db: Session, user_id: str):
    """
    Optimized SQL aggregate queries specifically for the User Dashboard overview.
    Uses Raw SQL for performance on MSSQL.
    """
    try:
        sql = text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM tasks
            WHERE assigned_to = CAST(:uid AS VARCHAR(50))
        """)
        
        with db.get_bind().connect() as connection:
            result = connection.execute(sql, {"uid": str(user_id)}).fetchone()
            
        total_tasks = int(result[0] or 0)
        completed_tasks = int(result[1] or 0)
        pending_tasks = total_tasks - completed_tasks
        
        return {
            "totalTasks": total_tasks,
            "completedTasks": completed_tasks,
            "pendingTasks": pending_tasks
        }
    except Exception as e:
        print(f"Error calculating user metrics: {e}")
        return {
            "totalTasks": 0, "completedTasks": 0, "pendingTasks": 0
        }
