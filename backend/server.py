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
    REFILL_DUE = "refill_due"
    PRESSURE_TEST_DUE = "pressure_test_due"
    MAINTENANCE = "maintenance"

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
    last_refill: datetime
    last_pressure_test: datetime
    next_refill_due: datetime
    next_pressure_test_due: datetime
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
    last_refill: Optional[datetime] = None
    last_pressure_test: Optional[datetime] = None

class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detector_id: str
    detector_name: str
    detector_location: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False

class AlertCreate(BaseModel):
    detector_id: str
    message: str

class AdminLogin(BaseModel):
    username: str
    password: str

# Helper functions
def calculate_due_dates(last_refill: datetime, last_pressure_test: datetime):
    next_refill_due = last_refill + timedelta(days=365)
    next_pressure_test_due = last_pressure_test + timedelta(days=365*3)
    return next_refill_due, next_pressure_test_due

def check_extinguisher_status(extinguisher: FireExtinguisher) -> ExtinguisherStatus:
    now = datetime.utcnow()
    days_until_refill = (extinguisher.next_refill_due - now).days
    days_until_pressure_test = (extinguisher.next_pressure_test_due - now).days
    
    if days_until_refill <= 30:
        return ExtinguisherStatus.REFILL_DUE
    elif days_until_pressure_test <= 30:
        return ExtinguisherStatus.PRESSURE_TEST_DUE
    else:
        return ExtinguisherStatus.ACTIVE

# Authentication endpoints
@api_router.post("/admin/login")
async def admin_login(login_data: AdminLogin):
    if login_data.username == ADMIN_USERNAME and login_data.password == ADMIN_PASSWORD:
        return {"message": "Login successful", "admin": True}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin credentials"
    )

@api_router.get("/admin/verify")
async def verify_admin(admin: str = Depends(get_current_admin)):
    return {"message": "Admin verified", "admin": admin}

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
    
    # Get recent alerts
    recent_alerts = await db.alerts.find({"acknowledged": False}).sort("timestamp", -1).limit(10).to_list(10)
    
    return {
        "detectors": {
            "total": total_detectors,
            "active": active_detectors,
            "triggered": triggered_detectors
        },
        "extinguishers": {
            "total": total_extinguishers
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