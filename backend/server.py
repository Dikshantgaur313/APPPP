from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from enum import Enum
import secrets

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBasic()
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "firesafety2025"
RESET_CODE = "APEX2025RESET"  # Simple reset code for demo

def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Enums
class DetectorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIGGERED = "triggered"
    MAINTENANCE = "maintenance"

class ExtinguisherStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    REFILL_DUE = "refill_due"
    PRESSURE_TEST_DUE = "pressure_test_due"
    MAINTENANCE = "maintenance"

class DispatchStatus(str, Enum):
    NONE = "none"
    DISPATCHED = "dispatched"
    UNDER_PROCESS = "under_process"
    RECEIVED = "received"

class MaintenanceItemStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

# Models
class SmokeDetector(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    location: str
    status: DetectorStatus = DetectorStatus.ACTIVE
    last_triggered: Optional[datetime] = None
    battery_level: int = 100
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SmokeDetectorCreate(BaseModel):
    name: str
    location: str
    battery_level: int = 100

class SmokeDetectorUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[DetectorStatus] = None
    battery_level: Optional[int] = None

class FireExtinguisher(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    location: str
    status: ExtinguisherStatus = ExtinguisherStatus.ACTIVE
    dispatch_status: DispatchStatus = DispatchStatus.NONE
    last_triggered: Optional[datetime] = None
    last_refill: datetime
    last_pressure_test: datetime
    next_refill_due: datetime
    next_pressure_test_due: datetime
    dispatch_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FireExtinguisherCreate(BaseModel):
    name: str
    location: str
    last_refill: datetime
    last_pressure_test: datetime

class FireExtinguisherUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[ExtinguisherStatus] = None
    dispatch_status: Optional[DispatchStatus] = None
    last_refill: Optional[datetime] = None
    last_pressure_test: Optional[datetime] = None

class MaintenanceNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    note: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"

class MaintenanceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    status: MaintenanceItemStatus = MaintenanceItemStatus.PENDING
    priority: str = "medium"  # low, medium, high
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: List[MaintenanceNote] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MaintenanceItemCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    priority: str = "medium"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

class MaintenanceItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[MaintenanceItemStatus] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

class MaintenanceNoteCreate(BaseModel):
    note: str

class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detector_id: Optional[str] = None
    extinguisher_id: Optional[str] = None
    detector_name: Optional[str] = None
    extinguisher_name: Optional[str] = None
    detector_location: Optional[str] = None
    extinguisher_location: Optional[str] = None
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False

class AlertCreate(BaseModel):
    detector_id: Optional[str] = None
    extinguisher_id: Optional[str] = None
    message: str

class AdminLogin(BaseModel):
    username: str
    password: str

class PasswordReset(BaseModel):
    reset_code: str
    new_password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Helper functions
def calculate_due_dates(last_refill: datetime, last_pressure_test: datetime):
    next_refill_due = last_refill + timedelta(days=365)
    next_pressure_test_due = last_pressure_test + timedelta(days=365*3)
    return next_refill_due, next_pressure_test_due

def check_extinguisher_status(extinguisher: FireExtinguisher) -> ExtinguisherStatus:
    if extinguisher.status == ExtinguisherStatus.TRIGGERED:
        return ExtinguisherStatus.TRIGGERED
    
    now = datetime.utcnow()
    days_until_refill = (extinguisher.next_refill_due - now).days
    days_until_pressure_test = (extinguisher.next_pressure_test_due - now).days
    
    if days_until_refill <= 30:
        return ExtinguisherStatus.REFILL_DUE
    elif days_until_pressure_test <= 30:
        return ExtinguisherStatus.PRESSURE_TEST_DUE
    else:
        return ExtinguisherStatus.ACTIVE

def is_extinguisher_due(extinguisher: FireExtinguisher) -> dict:
    now = datetime.utcnow()
    days_until_refill = (extinguisher.next_refill_due - now).days
    days_until_pressure_test = (extinguisher.next_pressure_test_due - now).days
    
    return {
        "refill_due": days_until_refill <= 30 or extinguisher.status == ExtinguisherStatus.TRIGGERED,
        "pressure_test_due": days_until_pressure_test <= 30,
        "days_until_refill": days_until_refill,
        "days_until_pressure_test": days_until_pressure_test
    }

def check_maintenance_item_status(item: MaintenanceItem) -> MaintenanceItemStatus:
    if item.status in [MaintenanceItemStatus.COMPLETED, MaintenanceItemStatus.IN_PROGRESS]:
        return item.status
    
    if item.due_date:
        now = datetime.utcnow()
        if now > item.due_date:
            return MaintenanceItemStatus.OVERDUE
    
    return MaintenanceItemStatus.PENDING

# Authentication endpoints
@api_router.post("/admin/login")
async def admin_login(login_data: AdminLogin):
    global ADMIN_PASSWORD
    if login_data.username == ADMIN_USERNAME and login_data.password == ADMIN_PASSWORD:
        return {"message": "Login successful", "admin": True}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin credentials"
    )

@api_router.get("/admin/verify")
async def verify_admin(admin: str = Depends(get_current_admin)):
    return {"message": "Admin verified", "admin": admin}

@api_router.post("/admin/reset-password")
async def reset_password(reset_data: PasswordReset):
    global ADMIN_PASSWORD
    if reset_data.reset_code == RESET_CODE:
        ADMIN_PASSWORD = reset_data.new_password
        return {"message": "Password reset successful"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid reset code"
    )

@api_router.post("/admin/change-password")
async def change_password(password_data: PasswordChange, admin: str = Depends(get_current_admin)):
    global ADMIN_PASSWORD
    if password_data.current_password == ADMIN_PASSWORD:
        ADMIN_PASSWORD = password_data.new_password
        return {"message": "Password changed successfully"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid current password"
    )

@api_router.get("/admin/reset-code")
async def get_reset_code():
    return {"reset_code": RESET_CODE, "message": "Use this code to reset admin password"}

# Public Smoke Detector endpoints (read-only)
@api_router.get("/smoke-detectors", response_model=List[SmokeDetector])
async def get_smoke_detectors():
    detectors = await db.smoke_detectors.find().to_list(1000)
    return [SmokeDetector(**detector) for detector in detectors]

@api_router.get("/smoke-detectors/{detector_id}", response_model=SmokeDetector)
async def get_smoke_detector(detector_id: str):
    detector = await db.smoke_detectors.find_one({"id": detector_id})
    if not detector:
        raise HTTPException(status_code=404, detail="Smoke detector not found")
    return SmokeDetector(**detector)

@api_router.post("/smoke-detectors/{detector_id}/trigger")
async def trigger_smoke_detector(detector_id: str):
    detector = await db.smoke_detectors.find_one({"id": detector_id})
    if not detector:
        raise HTTPException(status_code=404, detail="Smoke detector not found")
    
    # Update detector status
    now = datetime.utcnow()
    await db.smoke_detectors.update_one(
        {"id": detector_id},
        {"$set": {
            "status": DetectorStatus.TRIGGERED,
            "last_triggered": now,
            "updated_at": now
        }}
    )
    
    # Create alert
    alert = Alert(
        detector_id=detector_id,
        detector_name=detector["name"],
        detector_location=detector["location"],
        message=f"SMOKE DETECTED at {detector['location']} - {detector['name']}"
    )
    await db.alerts.insert_one(alert.dict())
    
    return {"message": "Smoke detector triggered successfully", "alert_id": alert.id}

@api_router.post("/smoke-detectors/{detector_id}/reset")
async def reset_smoke_detector(detector_id: str):
    detector = await db.smoke_detectors.find_one({"id": detector_id})
    if not detector:
        raise HTTPException(status_code=404, detail="Smoke detector not found")
    
    await db.smoke_detectors.update_one(
        {"id": detector_id},
        {"$set": {
            "status": DetectorStatus.ACTIVE,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Smoke detector reset successfully"}

# Admin-only Smoke Detector endpoints
@api_router.post("/admin/smoke-detectors", response_model=SmokeDetector)
async def create_smoke_detector(detector: SmokeDetectorCreate, admin: str = Depends(get_current_admin)):
    detector_dict = detector.dict()
    detector_obj = SmokeDetector(**detector_dict)
    await db.smoke_detectors.insert_one(detector_obj.dict())
    return detector_obj

@api_router.put("/admin/smoke-detectors/{detector_id}", response_model=SmokeDetector)
async def update_smoke_detector(detector_id: str, update_data: SmokeDetectorUpdate, admin: str = Depends(get_current_admin)):
    detector = await db.smoke_detectors.find_one({"id": detector_id})
    if not detector:
        raise HTTPException(status_code=404, detail="Smoke detector not found")
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.smoke_detectors.update_one(
        {"id": detector_id},
        {"$set": update_dict}
    )
    
    updated_detector = await db.smoke_detectors.find_one({"id": detector_id})
    return SmokeDetector(**updated_detector)

@api_router.delete("/admin/smoke-detectors/{detector_id}")
async def delete_smoke_detector(detector_id: str, admin: str = Depends(get_current_admin)):
    result = await db.smoke_detectors.delete_one({"id": detector_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Smoke detector not found")
    return {"message": "Smoke detector deleted successfully"}

# Public Fire Extinguisher endpoints (read-only)
@api_router.get("/fire-extinguishers", response_model=List[FireExtinguisher])
async def get_fire_extinguishers():
    extinguishers = await db.fire_extinguishers.find().to_list(1000)
    result = []
    for ext in extinguishers:
        ext_obj = FireExtinguisher(**ext)
        ext_obj.status = check_extinguisher_status(ext_obj)
        result.append(ext_obj)
    return result

@api_router.get("/fire-extinguishers/{extinguisher_id}", response_model=FireExtinguisher)
async def get_fire_extinguisher(extinguisher_id: str):
    extinguisher = await db.fire_extinguishers.find_one({"id": extinguisher_id})
    if not extinguisher:
        raise HTTPException(status_code=404, detail="Fire extinguisher not found")
    
    ext_obj = FireExtinguisher(**extinguisher)
    ext_obj.status = check_extinguisher_status(ext_obj)
    return ext_obj

# Public Fire Extinguisher action endpoints
@api_router.post("/fire-extinguishers/{extinguisher_id}/trigger")
async def trigger_fire_extinguisher(extinguisher_id: str):
    extinguisher = await db.fire_extinguishers.find_one({"id": extinguisher_id})
    if not extinguisher:
        raise HTTPException(status_code=404, detail="Fire extinguisher not found")
    
    # Update extinguisher status and set refill due to current date
    now = datetime.utcnow()
    next_refill_due, next_pressure_test_due = calculate_due_dates(now, extinguisher["last_pressure_test"])
    
    await db.fire_extinguishers.update_one(
        {"id": extinguisher_id},
        {"$set": {
            "status": ExtinguisherStatus.TRIGGERED,
            "last_triggered": now,
            "next_refill_due": now,  # Set refill due to current date
            "updated_at": now
        }}
    )
    
    # Create alert
    alert = Alert(
        extinguisher_id=extinguisher_id,
        extinguisher_name=extinguisher["name"],
        extinguisher_location=extinguisher["location"],
        message=f"FIRE EXTINGUISHER USED at {extinguisher['location']} - {extinguisher['name']} - REFILL REQUIRED"
    )
    await db.alerts.insert_one(alert.dict())
    
    return {"message": "Fire extinguisher triggered successfully", "alert_id": alert.id}

@api_router.post("/fire-extinguishers/{extinguisher_id}/refill")
async def refill_fire_extinguisher(extinguisher_id: str):
    extinguisher = await db.fire_extinguishers.find_one({"id": extinguisher_id})
    if not extinguisher:
        raise HTTPException(status_code=404, detail="Fire extinguisher not found")
    
    ext_obj = FireExtinguisher(**extinguisher)
    due_status = is_extinguisher_due(ext_obj)
    
    if not due_status["refill_due"]:
        raise HTTPException(status_code=400, detail="Fire extinguisher is not due for refill")
    
    # Update extinguisher with new refill date
    now = datetime.utcnow()
    next_refill_due, next_pressure_test_due = calculate_due_dates(now, extinguisher["last_pressure_test"])
    
    await db.fire_extinguishers.update_one(
        {"id": extinguisher_id},
        {"$set": {
            "last_refill": now,
            "next_refill_due": next_refill_due,
            "status": ExtinguisherStatus.ACTIVE,
            "updated_at": now
        }}
    )
    
    return {"message": "Fire extinguisher refilled successfully"}

@api_router.post("/fire-extinguishers/{extinguisher_id}/pressure-test")
async def pressure_test_fire_extinguisher(extinguisher_id: str):
    extinguisher = await db.fire_extinguishers.find_one({"id": extinguisher_id})
    if not extinguisher:
        raise HTTPException(status_code=404, detail="Fire extinguisher not found")
    
    ext_obj = FireExtinguisher(**extinguisher)
    due_status = is_extinguisher_due(ext_obj)
    
    if not due_status["pressure_test_due"]:
        raise HTTPException(status_code=400, detail="Fire extinguisher is not due for pressure test")
    
    # Update extinguisher with new pressure test date
    now = datetime.utcnow()
    next_refill_due, next_pressure_test_due = calculate_due_dates(extinguisher["last_refill"], now)
    
    await db.fire_extinguishers.update_one(
        {"id": extinguisher_id},
        {"$set": {
            "last_pressure_test": now,
            "next_pressure_test_due": next_pressure_test_due,
            "status": ExtinguisherStatus.ACTIVE,
            "updated_at": now
        }}
    )
    
    return {"message": "Fire extinguisher pressure test completed successfully"}

@api_router.get("/fire-extinguishers/{extinguisher_id}/due-status")
async def get_extinguisher_due_status(extinguisher_id: str):
    extinguisher = await db.fire_extinguishers.find_one({"id": extinguisher_id})
    if not extinguisher:
        raise HTTPException(status_code=404, detail="Fire extinguisher not found")
    
    ext_obj = FireExtinguisher(**extinguisher)
    due_status = is_extinguisher_due(ext_obj)
    
    return due_status

# Admin-only Fire Extinguisher endpoints
@api_router.post("/admin/fire-extinguishers", response_model=FireExtinguisher)
async def create_fire_extinguisher(extinguisher: FireExtinguisherCreate, admin: str = Depends(get_current_admin)):
    extinguisher_dict = extinguisher.dict()
    next_refill_due, next_pressure_test_due = calculate_due_dates(
        extinguisher_dict["last_refill"],
        extinguisher_dict["last_pressure_test"]
    )
    
    extinguisher_obj = FireExtinguisher(
        **extinguisher_dict,
        next_refill_due=next_refill_due,
        next_pressure_test_due=next_pressure_test_due
    )
    
    # Check status
    extinguisher_obj.status = check_extinguisher_status(extinguisher_obj)
    
    await db.fire_extinguishers.insert_one(extinguisher_obj.dict())
    return extinguisher_obj

@api_router.put("/admin/fire-extinguishers/{extinguisher_id}", response_model=FireExtinguisher)
async def update_fire_extinguisher(extinguisher_id: str, update_data: FireExtinguisherUpdate, admin: str = Depends(get_current_admin)):
    extinguisher = await db.fire_extinguishers.find_one({"id": extinguisher_id})
    if not extinguisher:
        raise HTTPException(status_code=404, detail="Fire extinguisher not found")
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    # Recalculate due dates if refill or pressure test dates are updated
    if "last_refill" in update_dict or "last_pressure_test" in update_dict:
        last_refill = update_dict.get("last_refill", extinguisher["last_refill"])
        last_pressure_test = update_dict.get("last_pressure_test", extinguisher["last_pressure_test"])
        next_refill_due, next_pressure_test_due = calculate_due_dates(last_refill, last_pressure_test)
        update_dict["next_refill_due"] = next_refill_due
        update_dict["next_pressure_test_due"] = next_pressure_test_due
    
    await db.fire_extinguishers.update_one(
        {"id": extinguisher_id},
        {"$set": update_dict}
    )
    
    updated_extinguisher = await db.fire_extinguishers.find_one({"id": extinguisher_id})
    ext_obj = FireExtinguisher(**updated_extinguisher)
    ext_obj.status = check_extinguisher_status(ext_obj)
    return ext_obj

@api_router.delete("/admin/fire-extinguishers/{extinguisher_id}")
async def delete_fire_extinguisher(extinguisher_id: str, admin: str = Depends(get_current_admin)):
    result = await db.fire_extinguishers.delete_one({"id": extinguisher_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fire extinguisher not found")
    return {"message": "Fire extinguisher deleted successfully"}

# Maintenance Items endpoints
@api_router.get("/maintenance-items", response_model=List[MaintenanceItem])
async def get_maintenance_items():
    items = await db.maintenance_items.find().sort("created_at", -1).to_list(1000)
    result = []
    for item in items:
        item_obj = MaintenanceItem(**item)
        item_obj.status = check_maintenance_item_status(item_obj)
        result.append(item_obj)
    return result

@api_router.get("/maintenance-items/{item_id}", response_model=MaintenanceItem)
async def get_maintenance_item(item_id: str):
    item = await db.maintenance_items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Maintenance item not found")
    
    item_obj = MaintenanceItem(**item)
    item_obj.status = check_maintenance_item_status(item_obj)
    return item_obj

@api_router.post("/maintenance-items", response_model=MaintenanceItem)
async def create_maintenance_item(item: MaintenanceItemCreate):
    item_dict = item.dict()
    item_obj = MaintenanceItem(**item_dict)
    item_obj.status = check_maintenance_item_status(item_obj)
    await db.maintenance_items.insert_one(item_obj.dict())
    return item_obj

@api_router.put("/maintenance-items/{item_id}", response_model=MaintenanceItem)
async def update_maintenance_item(item_id: str, update_data: MaintenanceItemUpdate):
    item = await db.maintenance_items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Maintenance item not found")
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.maintenance_items.update_one(
        {"id": item_id},
        {"$set": update_dict}
    )
    
    updated_item = await db.maintenance_items.find_one({"id": item_id})
    item_obj = MaintenanceItem(**updated_item)
    item_obj.status = check_maintenance_item_status(item_obj)
    return item_obj

@api_router.delete("/maintenance-items/{item_id}")
async def delete_maintenance_item(item_id: str):
    result = await db.maintenance_items.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Maintenance item not found")
    return {"message": "Maintenance item deleted successfully"}

@api_router.post("/maintenance-items/{item_id}/notes", response_model=MaintenanceItem)
async def add_maintenance_note(item_id: str, note_data: MaintenanceNoteCreate):
    item = await db.maintenance_items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Maintenance item not found")
    
    new_note = MaintenanceNote(note=note_data.note, created_by="user")
    
    await db.maintenance_items.update_one(
        {"id": item_id},
        {
            "$push": {"notes": new_note.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    updated_item = await db.maintenance_items.find_one({"id": item_id})
    item_obj = MaintenanceItem(**updated_item)
    item_obj.status = check_maintenance_item_status(item_obj)
    return item_obj

# Alert endpoints
@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts():
    alerts = await db.alerts.find().sort("timestamp", -1).to_list(1000)
    return [Alert(**alert) for alert in alerts]

@api_router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    result = await db.alerts.update_one(
        {"id": alert_id},
        {"$set": {"acknowledged": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert acknowledged"}

@api_router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    result = await db.alerts.delete_one({"id": alert_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted successfully"}

# Dashboard endpoint
@api_router.get("/dashboard")
async def get_dashboard():
    # Get detector stats
    total_detectors = await db.smoke_detectors.count_documents({})
    active_detectors = await db.smoke_detectors.count_documents({"status": "active"})
    triggered_detectors = await db.smoke_detectors.count_documents({"status": "triggered"})
    
    # Get extinguisher stats
    total_extinguishers = await db.fire_extinguishers.count_documents({})
    triggered_extinguishers = await db.fire_extinguishers.count_documents({"status": "triggered"})
    
    # Get maintenance stats
    total_maintenance = await db.maintenance_items.count_documents({})
    pending_maintenance = await db.maintenance_items.count_documents({"status": "pending"})
    overdue_maintenance = await db.maintenance_items.count_documents({"status": "overdue"})
    
    # Get recent alerts
    recent_alerts = await db.alerts.find({"acknowledged": False}).sort("timestamp", -1).limit(10).to_list(10)
    
    return {
        "detectors": {
            "total": total_detectors,
            "active": active_detectors,
            "triggered": triggered_detectors
        },
        "extinguishers": {
            "total": total_extinguishers,
            "triggered": triggered_extinguishers
        },
        "maintenance": {
            "total": total_maintenance,
            "pending": pending_maintenance,
            "overdue": overdue_maintenance
        },
        "recent_alerts": [Alert(**alert) for alert in recent_alerts]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()