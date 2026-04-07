from pydantic import BaseModel, EmailStr, Field, computed_field
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# ======== AUTH ========
class LoginRequest(BaseModel):
    email: Optional[str] = None
    employee_id: Optional[str] = None
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    employeeId: Optional[str] = Field(None, validation_alias="employee_id")
    name: str
    email: Optional[str] = None
    role: str
    avatar: Optional[str] = None
    projectId: Optional[str] = Field(None, validation_alias="project_id")
    
    class Config:
        populate_by_name = True
        from_attributes = True

# ======== PROJECT ========
class ProjectCreate(BaseModel):
    name: str
    image: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    image: Optional[str] = None
    createdAt: Optional[datetime] = Field(None, validation_alias="created_at")
    updatedAt: Optional[datetime] = Field(None, validation_alias="updated_at")  # 🔥 FIX

    class Config:
        populate_by_name = True
        from_attributes = True

# ======== EMPLOYEE / USER ========
class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    role: str = "user"
    project_id: Optional[str] = None

class EmployeeProgressUpdate(BaseModel):
    dailyProgress: float
    weeklyProgress: float

class EmployeeResponse(UserResponse):
    dailyProgress: float = Field(0.0, validation_alias="daily_progress")
    weeklyProgress: float = Field(0.0, validation_alias="weekly_progress")
    createdAt: Optional[datetime] = Field(None, validation_alias="created_at")

    class Config:
        populate_by_name = True
        from_attributes = True

# ======== TASK ========
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "Medium"
    timeline: str = "daily"
    assignedTo: str
    projectId: str

class TaskStatusUpdate(BaseModel):
    status: str # 'Pending', 'In Progress', 'Completed'

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: str
    status: str
    timeline: str
    assignedTo: str = Field(..., validation_alias="assigned_to")
    projectId: str = Field(..., validation_alias="project_id")
    createdAt: Optional[datetime] = Field(None, validation_alias="created_at")

    class Config:
        populate_by_name = True
        from_attributes = True

# ======== ATTENDANCE ========
class CheckInRequest(BaseModel):
    employee_id: str
    date: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AttendanceResponse(BaseModel):
    id: str
    userId: str = Field(..., validation_alias="employee_id")
    employeeId: str = Field(..., validation_alias="employee_id")
    userName: Optional[str] = None
    date: str
    checkIn: Optional[str] = Field(None, validation_alias="check_in")
    checkOut: Optional[str] = Field(None, validation_alias="check_out")
    locationName: Optional[str] = Field(None, validation_alias="location_name")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    createdAt: Optional[datetime] = Field(None, validation_alias="created_at")

    @computed_field
    @property
    def status(self) -> str:
        return "Checked In" if not self.checkOut else "Checked Out"

    @computed_field
    @property
    def checkInTime(self) -> Optional[str]:
        return self.checkIn

    @computed_field
    @property
    def checkOutTime(self) -> Optional[str]:
        return self.checkOut

    class Config:
        populate_by_name = True
        from_attributes = True

# ======== DASHBOARD ========
class DashboardMetricsResponse(BaseModel):
    activeProjects: int
    totalTasks: int
    completedTasks: int
    activeEmployees: int

# ======== OFFER LETTER ========
class OfferLetterCreate(BaseModel):
    employee_id: str
    employee_name: str
    role: str
    joining_date: str
    location: str
    package: str
    project_id: Optional[str] = None

class OfferLetterResponse(BaseModel):
    id: str
    employee_id: str = Field(..., validation_alias="employee_id")
    employee_name: str = Field(..., validation_alias="name")
    role: str
    joining_date: str
    location: str
    package: str
    projectId: Optional[str] = Field(None, validation_alias="project_id")
    created_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True

# ======== LEAVE REQUEST ========
class LeaveRequestCreate(BaseModel):
    employee_id: str
    leave_type: str
    from_date: str
    to_date: str
    reason: str

class LeaveRequestResponse(BaseModel):
    id: str
    employeeId: str = Field(..., validation_alias="employee_id")
    userName: Optional[str] = None
    leave_type: str
    from_date: str
    to_date: str
    reason: Optional[str] = None
    status: Optional[str] = "Pending"
    created_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True

class ProjectResponse(BaseModel):
    id: str
    name: str
    image: Optional[str] = None
    createdAt: Optional[datetime] = Field(None, validation_alias="created_at")
    updatedAt: Optional[datetime] = Field(None, validation_alias="updated_at")

    class Config:
        populate_by_name = True
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}  # 🔥 ADD THIS

# ======== PAY SLIP ========
class PaySlipCreate(BaseModel):
    employee_id: str
    month: str
    amount: str
    status: str = "Generated"
    project_id: Optional[str] = None

class PaySlipResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = Field(None, validation_alias="employee_name")
    month: str
    amount: str
    status: str
    created_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
