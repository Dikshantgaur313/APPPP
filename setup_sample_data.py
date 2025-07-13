#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid

# MongoDB connection
mongo_url = "mongodb://localhost:27017"
client = AsyncIOMotorClient(mongo_url)
db = client["test_database"]

async def setup_sample_data():
    print("Setting up sample data for Fire Safety Management System...")
    
    # Clear existing data
    await db.smoke_detectors.delete_many({})
    await db.fire_extinguishers.delete_many({})
    await db.alerts.delete_many({})
    
    # Sample smoke detectors
    smoke_detectors = [
        {
            "id": str(uuid.uuid4()),
            "name": "Smoke Detector A1",
            "location": "Main Office - Floor 1",
            "status": "active",
            "last_triggered": None,
            "battery_level": 85,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smoke Detector B2",
            "location": "Kitchen - Floor 2",
            "status": "active",
            "last_triggered": None,
            "battery_level": 92,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smoke Detector C3",
            "location": "Server Room - Basement",
            "status": "active",
            "last_triggered": None,
            "battery_level": 78,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smoke Detector D4",
            "location": "Conference Room - Floor 3",
            "status": "active",
            "last_triggered": None,
            "battery_level": 95,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Sample fire extinguishers
    base_date = datetime.utcnow()
    fire_extinguishers = [
        {
            "id": str(uuid.uuid4()),
            "name": "Fire Extinguisher FE-001",
            "location": "Main Lobby - Floor 1",
            "status": "active",
            "last_refill": base_date - timedelta(days=30),
            "last_pressure_test": base_date - timedelta(days=365),
            "next_refill_due": base_date - timedelta(days=30) + timedelta(days=365),
            "next_pressure_test_due": base_date - timedelta(days=365) + timedelta(days=365*3),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fire Extinguisher FE-002",
            "location": "Kitchen - Floor 2",
            "status": "active",
            "last_refill": base_date - timedelta(days=350),
            "last_pressure_test": base_date - timedelta(days=730),
            "next_refill_due": base_date - timedelta(days=350) + timedelta(days=365),
            "next_pressure_test_due": base_date - timedelta(days=730) + timedelta(days=365*3),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fire Extinguisher FE-003",
            "location": "Server Room - Basement",
            "status": "active",
            "last_refill": base_date - timedelta(days=180),
            "last_pressure_test": base_date - timedelta(days=1095),
            "next_refill_due": base_date - timedelta(days=180) + timedelta(days=365),
            "next_pressure_test_due": base_date - timedelta(days=1095) + timedelta(days=365*3),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fire Extinguisher FE-004",
            "location": "Emergency Exit - Floor 3",
            "status": "active",
            "last_refill": base_date - timedelta(days=90),
            "last_pressure_test": base_date - timedelta(days=200),
            "next_refill_due": base_date - timedelta(days=90) + timedelta(days=365),
            "next_pressure_test_due": base_date - timedelta(days=200) + timedelta(days=365*3),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert sample data
    await db.smoke_detectors.insert_many(smoke_detectors)
    await db.fire_extinguishers.insert_many(fire_extinguishers)
    
    print(f"✅ Inserted {len(smoke_detectors)} smoke detectors")
    print(f"✅ Inserted {len(fire_extinguishers)} fire extinguishers")
    print("🔥 Fire Safety Management System is ready!")

if __name__ == "__main__":
    asyncio.run(setup_sample_data())