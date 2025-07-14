#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Fire Safety Management System
Tests all CRUD operations, trigger system, alert management, and dashboard
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Testing API at: {API_URL}")

# Test results tracking
test_results = {
    "smoke_detector_crud": {"passed": 0, "failed": 0, "errors": []},
    "fire_extinguisher_crud": {"passed": 0, "failed": 0, "errors": []},
    "smoke_detector_trigger": {"passed": 0, "failed": 0, "errors": []},
    "alert_management": {"passed": 0, "failed": 0, "errors": []},
    "dashboard_api": {"passed": 0, "failed": 0, "errors": []},
    "dispatch_functionality": {"passed": 0, "failed": 0, "errors": []}
}

def log_test(category, test_name, success, error_msg=None):
    """Log test results"""
    if success:
        test_results[category]["passed"] += 1
        print(f"✅ {test_name}")
    else:
        test_results[category]["failed"] += 1
        test_results[category]["errors"].append(f"{test_name}: {error_msg}")
        print(f"❌ {test_name}: {error_msg}")

def test_smoke_detector_crud():
    """Test Smoke Detector CRUD Operations"""
    print("\n=== Testing Smoke Detector CRUD Operations ===")
    
    # Test CREATE
    try:
        create_data = {
            "name": "Kitchen Smoke Detector",
            "location": "Kitchen Area",
            "battery_level": 85
        }
        response = requests.post(f"{API_URL}/smoke-detectors", json=create_data)
        if response.status_code == 200:
            detector = response.json()
            detector_id = detector["id"]
            log_test("smoke_detector_crud", "Create smoke detector", True)
        else:
            log_test("smoke_detector_crud", "Create smoke detector", False, f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("smoke_detector_crud", "Create smoke detector", False, str(e))
        return

    # Test READ ALL
    try:
        response = requests.get(f"{API_URL}/smoke-detectors")
        if response.status_code == 200:
            detectors = response.json()
            if isinstance(detectors, list) and len(detectors) > 0:
                log_test("smoke_detector_crud", "Get all smoke detectors", True)
            else:
                log_test("smoke_detector_crud", "Get all smoke detectors", False, "Empty or invalid response")
        else:
            log_test("smoke_detector_crud", "Get all smoke detectors", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("smoke_detector_crud", "Get all smoke detectors", False, str(e))

    # Test READ ONE
    try:
        response = requests.get(f"{API_URL}/smoke-detectors/{detector_id}")
        if response.status_code == 200:
            detector = response.json()
            if detector["id"] == detector_id:
                log_test("smoke_detector_crud", "Get single smoke detector", True)
            else:
                log_test("smoke_detector_crud", "Get single smoke detector", False, "ID mismatch")
        else:
            log_test("smoke_detector_crud", "Get single smoke detector", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("smoke_detector_crud", "Get single smoke detector", False, str(e))

    # Test UPDATE
    try:
        update_data = {
            "name": "Updated Kitchen Detector",
            "battery_level": 75
        }
        response = requests.put(f"{API_URL}/smoke-detectors/{detector_id}", json=update_data)
        if response.status_code == 200:
            updated_detector = response.json()
            if updated_detector["name"] == "Updated Kitchen Detector" and updated_detector["battery_level"] == 75:
                log_test("smoke_detector_crud", "Update smoke detector", True)
            else:
                log_test("smoke_detector_crud", "Update smoke detector", False, "Update not reflected")
        else:
            log_test("smoke_detector_crud", "Update smoke detector", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("smoke_detector_crud", "Update smoke detector", False, str(e))

    # Test DELETE
    try:
        response = requests.delete(f"{API_URL}/smoke-detectors/{detector_id}")
        if response.status_code == 200:
            # Verify deletion
            verify_response = requests.get(f"{API_URL}/smoke-detectors/{detector_id}")
            if verify_response.status_code == 404:
                log_test("smoke_detector_crud", "Delete smoke detector", True)
            else:
                log_test("smoke_detector_crud", "Delete smoke detector", False, "Detector still exists after deletion")
        else:
            log_test("smoke_detector_crud", "Delete smoke detector", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("smoke_detector_crud", "Delete smoke detector", False, str(e))

def test_fire_extinguisher_crud():
    """Test Fire Extinguisher CRUD Operations"""
    print("\n=== Testing Fire Extinguisher CRUD Operations ===")
    
    # Test CREATE with automatic due date calculation
    try:
        now = datetime.utcnow()
        create_data = {
            "name": "Office Fire Extinguisher",
            "location": "Main Office",
            "last_refill": (now - timedelta(days=30)).isoformat(),
            "last_pressure_test": (now - timedelta(days=60)).isoformat()
        }
        response = requests.post(f"{API_URL}/fire-extinguishers", json=create_data)
        if response.status_code == 200:
            extinguisher = response.json()
            extinguisher_id = extinguisher["id"]
            # Verify due dates are calculated
            if "next_refill_due" in extinguisher and "next_pressure_test_due" in extinguisher:
                log_test("fire_extinguisher_crud", "Create fire extinguisher with due dates", True)
            else:
                log_test("fire_extinguisher_crud", "Create fire extinguisher with due dates", False, "Due dates not calculated")
        else:
            log_test("fire_extinguisher_crud", "Create fire extinguisher with due dates", False, f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("fire_extinguisher_crud", "Create fire extinguisher with due dates", False, str(e))
        return

    # Test READ ALL
    try:
        response = requests.get(f"{API_URL}/fire-extinguishers")
        if response.status_code == 200:
            extinguishers = response.json()
            if isinstance(extinguishers, list) and len(extinguishers) > 0:
                log_test("fire_extinguisher_crud", "Get all fire extinguishers", True)
            else:
                log_test("fire_extinguisher_crud", "Get all fire extinguishers", False, "Empty or invalid response")
        else:
            log_test("fire_extinguisher_crud", "Get all fire extinguishers", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("fire_extinguisher_crud", "Get all fire extinguishers", False, str(e))

    # Test READ ONE
    try:
        response = requests.get(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
        if response.status_code == 200:
            extinguisher = response.json()
            if extinguisher["id"] == extinguisher_id:
                log_test("fire_extinguisher_crud", "Get single fire extinguisher", True)
            else:
                log_test("fire_extinguisher_crud", "Get single fire extinguisher", False, "ID mismatch")
        else:
            log_test("fire_extinguisher_crud", "Get single fire extinguisher", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("fire_extinguisher_crud", "Get single fire extinguisher", False, str(e))

    # Test UPDATE with due date recalculation
    try:
        new_refill_date = datetime.utcnow() - timedelta(days=10)
        update_data = {
            "name": "Updated Office Extinguisher",
            "last_refill": new_refill_date.isoformat()
        }
        response = requests.put(f"{API_URL}/fire-extinguishers/{extinguisher_id}", json=update_data)
        if response.status_code == 200:
            updated_extinguisher = response.json()
            if updated_extinguisher["name"] == "Updated Office Extinguisher":
                log_test("fire_extinguisher_crud", "Update fire extinguisher", True)
            else:
                log_test("fire_extinguisher_crud", "Update fire extinguisher", False, "Update not reflected")
        else:
            log_test("fire_extinguisher_crud", "Update fire extinguisher", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("fire_extinguisher_crud", "Update fire extinguisher", False, str(e))

    # Test DELETE
    try:
        response = requests.delete(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
        if response.status_code == 200:
            # Verify deletion
            verify_response = requests.get(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
            if verify_response.status_code == 404:
                log_test("fire_extinguisher_crud", "Delete fire extinguisher", True)
            else:
                log_test("fire_extinguisher_crud", "Delete fire extinguisher", False, "Extinguisher still exists after deletion")
        else:
            log_test("fire_extinguisher_crud", "Delete fire extinguisher", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("fire_extinguisher_crud", "Delete fire extinguisher", False, str(e))

def test_smoke_detector_trigger_system():
    """Test Smoke Detector Trigger and Reset System"""
    print("\n=== Testing Smoke Detector Trigger System ===")
    
    # First create a detector for testing
    try:
        create_data = {
            "name": "Test Trigger Detector",
            "location": "Test Area",
            "battery_level": 90
        }
        response = requests.post(f"{API_URL}/smoke-detectors", json=create_data)
        if response.status_code == 200:
            detector = response.json()
            detector_id = detector["id"]
        else:
            log_test("smoke_detector_trigger", "Setup test detector", False, f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("smoke_detector_trigger", "Setup test detector", False, str(e))
        return

    # Test TRIGGER
    try:
        response = requests.post(f"{API_URL}/smoke-detectors/{detector_id}/trigger")
        if response.status_code == 200:
            result = response.json()
            if "alert_id" in result:
                alert_id = result["alert_id"]
                log_test("smoke_detector_trigger", "Trigger smoke detector", True)
                
                # Verify detector status changed to triggered
                detector_response = requests.get(f"{API_URL}/smoke-detectors/{detector_id}")
                if detector_response.status_code == 200:
                    detector = detector_response.json()
                    if detector["status"] == "triggered" and detector["last_triggered"]:
                        log_test("smoke_detector_trigger", "Verify detector status after trigger", True)
                    else:
                        log_test("smoke_detector_trigger", "Verify detector status after trigger", False, "Status not updated")
                else:
                    log_test("smoke_detector_trigger", "Verify detector status after trigger", False, "Could not fetch detector")
            else:
                log_test("smoke_detector_trigger", "Trigger smoke detector", False, "No alert_id returned")
        else:
            log_test("smoke_detector_trigger", "Trigger smoke detector", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("smoke_detector_trigger", "Trigger smoke detector", False, str(e))

    # Test RESET
    try:
        response = requests.post(f"{API_URL}/smoke-detectors/{detector_id}/reset")
        if response.status_code == 200:
            log_test("smoke_detector_trigger", "Reset smoke detector", True)
            
            # Verify detector status changed back to active
            detector_response = requests.get(f"{API_URL}/smoke-detectors/{detector_id}")
            if detector_response.status_code == 200:
                detector = detector_response.json()
                if detector["status"] == "active":
                    log_test("smoke_detector_trigger", "Verify detector status after reset", True)
                else:
                    log_test("smoke_detector_trigger", "Verify detector status after reset", False, f"Status is {detector['status']}, expected active")
            else:
                log_test("smoke_detector_trigger", "Verify detector status after reset", False, "Could not fetch detector")
        else:
            log_test("smoke_detector_trigger", "Reset smoke detector", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("smoke_detector_trigger", "Reset smoke detector", False, str(e))

    # Cleanup
    try:
        requests.delete(f"{API_URL}/smoke-detectors/{detector_id}")
    except:
        pass

def test_alert_management():
    """Test Alert Management System"""
    print("\n=== Testing Alert Management System ===")
    
    # Create a detector and trigger it to generate an alert
    try:
        create_data = {
            "name": "Alert Test Detector",
            "location": "Alert Test Area",
            "battery_level": 95
        }
        response = requests.post(f"{API_URL}/smoke-detectors", json=create_data)
        detector = response.json()
        detector_id = detector["id"]
        
        # Trigger to create alert
        requests.post(f"{API_URL}/smoke-detectors/{detector_id}/trigger")
        time.sleep(1)  # Small delay to ensure alert is created
    except Exception as e:
        log_test("alert_management", "Setup alert for testing", False, str(e))
        return

    # Test GET ALERTS
    try:
        response = requests.get(f"{API_URL}/alerts")
        if response.status_code == 200:
            alerts = response.json()
            if isinstance(alerts, list) and len(alerts) > 0:
                alert_id = alerts[0]["id"]
                log_test("alert_management", "Get alerts list", True)
                
                # Verify alert structure
                alert = alerts[0]
                required_fields = ["id", "detector_id", "detector_name", "detector_location", "message", "timestamp", "acknowledged"]
                if all(field in alert for field in required_fields):
                    log_test("alert_management", "Verify alert structure", True)
                else:
                    log_test("alert_management", "Verify alert structure", False, "Missing required fields")
            else:
                log_test("alert_management", "Get alerts list", False, "No alerts found")
                return
        else:
            log_test("alert_management", "Get alerts list", False, f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("alert_management", "Get alerts list", False, str(e))
        return

    # Test ACKNOWLEDGE ALERT
    try:
        response = requests.put(f"{API_URL}/alerts/{alert_id}/acknowledge")
        if response.status_code == 200:
            log_test("alert_management", "Acknowledge alert", True)
            
            # Verify acknowledgment
            alerts_response = requests.get(f"{API_URL}/alerts")
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                acknowledged_alert = next((a for a in alerts if a["id"] == alert_id), None)
                if acknowledged_alert and acknowledged_alert["acknowledged"]:
                    log_test("alert_management", "Verify alert acknowledgment", True)
                else:
                    log_test("alert_management", "Verify alert acknowledgment", False, "Alert not marked as acknowledged")
            else:
                log_test("alert_management", "Verify alert acknowledgment", False, "Could not fetch alerts")
        else:
            log_test("alert_management", "Acknowledge alert", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("alert_management", "Acknowledge alert", False, str(e))

    # Test DELETE ALERT
    try:
        response = requests.delete(f"{API_URL}/alerts/{alert_id}")
        if response.status_code == 200:
            log_test("alert_management", "Delete alert", True)
            
            # Verify deletion
            alerts_response = requests.get(f"{API_URL}/alerts")
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                deleted_alert = next((a for a in alerts if a["id"] == alert_id), None)
                if not deleted_alert:
                    log_test("alert_management", "Verify alert deletion", True)
                else:
                    log_test("alert_management", "Verify alert deletion", False, "Alert still exists after deletion")
            else:
                log_test("alert_management", "Verify alert deletion", False, "Could not fetch alerts")
        else:
            log_test("alert_management", "Delete alert", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("alert_management", "Delete alert", False, str(e))

    # Cleanup
    try:
        requests.delete(f"{API_URL}/smoke-detectors/{detector_id}")
    except:
        pass

def test_dashboard_api():
    """Test Dashboard API with Statistics"""
    print("\n=== Testing Dashboard API ===")
    
    # Create some test data first
    try:
        # Create detectors
        detector_data = [
            {"name": "Dashboard Test Detector 1", "location": "Area 1", "battery_level": 80},
            {"name": "Dashboard Test Detector 2", "location": "Area 2", "battery_level": 90}
        ]
        detector_ids = []
        for data in detector_data:
            response = requests.post(f"{API_URL}/smoke-detectors", json=data)
            if response.status_code == 200:
                detector_ids.append(response.json()["id"])
        
        # Create extinguisher
        now = datetime.utcnow()
        extinguisher_data = {
            "name": "Dashboard Test Extinguisher",
            "location": "Test Area",
            "last_refill": (now - timedelta(days=30)).isoformat(),
            "last_pressure_test": (now - timedelta(days=60)).isoformat()
        }
        ext_response = requests.post(f"{API_URL}/fire-extinguishers", json=extinguisher_data)
        extinguisher_id = ext_response.json()["id"] if ext_response.status_code == 200 else None
        
        # Trigger one detector to create alert
        if detector_ids:
            requests.post(f"{API_URL}/smoke-detectors/{detector_ids[0]}/trigger")
        
        time.sleep(1)  # Allow data to be processed
    except Exception as e:
        log_test("dashboard_api", "Setup dashboard test data", False, str(e))

    # Test DASHBOARD ENDPOINT
    try:
        response = requests.get(f"{API_URL}/dashboard")
        if response.status_code == 200:
            dashboard = response.json()
            
            # Verify dashboard structure
            required_sections = ["detectors", "extinguishers", "recent_alerts"]
            if all(section in dashboard for section in required_sections):
                log_test("dashboard_api", "Dashboard structure", True)
                
                # Verify detector stats
                detector_stats = dashboard["detectors"]
                if "total" in detector_stats and "active" in detector_stats and "triggered" in detector_stats:
                    if detector_stats["total"] >= 2:  # We created 2 detectors
                        log_test("dashboard_api", "Detector statistics accuracy", True)
                    else:
                        log_test("dashboard_api", "Detector statistics accuracy", False, f"Expected >= 2 total detectors, got {detector_stats['total']}")
                else:
                    log_test("dashboard_api", "Detector statistics structure", False, "Missing detector stat fields")
                
                # Verify extinguisher stats
                extinguisher_stats = dashboard["extinguishers"]
                if "total" in extinguisher_stats:
                    if extinguisher_stats["total"] >= 1:  # We created 1 extinguisher
                        log_test("dashboard_api", "Extinguisher statistics accuracy", True)
                    else:
                        log_test("dashboard_api", "Extinguisher statistics accuracy", False, f"Expected >= 1 total extinguishers, got {extinguisher_stats['total']}")
                else:
                    log_test("dashboard_api", "Extinguisher statistics structure", False, "Missing extinguisher total field")
                
                # Verify recent alerts
                recent_alerts = dashboard["recent_alerts"]
                if isinstance(recent_alerts, list):
                    log_test("dashboard_api", "Recent alerts structure", True)
                    if len(recent_alerts) > 0:
                        alert = recent_alerts[0]
                        alert_fields = ["id", "detector_id", "detector_name", "message", "timestamp", "acknowledged"]
                        if all(field in alert for field in alert_fields):
                            log_test("dashboard_api", "Alert data completeness", True)
                        else:
                            log_test("dashboard_api", "Alert data completeness", False, "Missing alert fields")
                    else:
                        log_test("dashboard_api", "Recent alerts data", False, "No recent alerts found")
                else:
                    log_test("dashboard_api", "Recent alerts structure", False, "Recent alerts is not a list")
            else:
                log_test("dashboard_api", "Dashboard structure", False, "Missing required sections")
        else:
            log_test("dashboard_api", "Dashboard endpoint", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("dashboard_api", "Dashboard endpoint", False, str(e))

    # Cleanup test data
    try:
        for detector_id in detector_ids:
            requests.delete(f"{API_URL}/smoke-detectors/{detector_id}")
        if extinguisher_id:
            requests.delete(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
    except:
        pass

def test_dispatch_functionality():
    """Test Fire Extinguisher Dispatch Functionality"""
    print("\n=== Testing Fire Extinguisher Dispatch Functionality ===")
    
    # First create a fire extinguisher for testing
    try:
        now = datetime.utcnow()
        create_data = {
            "name": "Dispatch Test Extinguisher",
            "location": "Dispatch Test Area",
            "last_refill": (now - timedelta(days=30)).isoformat(),
            "last_pressure_test": (now - timedelta(days=60)).isoformat()
        }
        response = requests.post(f"{API_URL}/fire-extinguishers", json=create_data)
        if response.status_code == 200:
            extinguisher = response.json()
            extinguisher_id = extinguisher["id"]
            log_test("dispatch_functionality", "Setup test extinguisher", True)
        else:
            log_test("dispatch_functionality", "Setup test extinguisher", False, f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("dispatch_functionality", "Setup test extinguisher", False, str(e))
        return

    # Test 1: Dispatch an extinguisher
    try:
        response = requests.post(f"{API_URL}/fire-extinguishers/{extinguisher_id}/dispatch")
        if response.status_code == 200:
            result = response.json()
            if "message" in result and "dispatched successfully" in result["message"]:
                log_test("dispatch_functionality", "Dispatch extinguisher", True)
                
                # Verify dispatch status was updated
                ext_response = requests.get(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
                if ext_response.status_code == 200:
                    ext_data = ext_response.json()
                    if ext_data["dispatch_status"] == "dispatched" and ext_data["dispatch_date"]:
                        log_test("dispatch_functionality", "Verify dispatch status after dispatch", True)
                    else:
                        log_test("dispatch_functionality", "Verify dispatch status after dispatch", False, f"Status: {ext_data['dispatch_status']}")
                else:
                    log_test("dispatch_functionality", "Verify dispatch status after dispatch", False, "Could not fetch extinguisher")
            else:
                log_test("dispatch_functionality", "Dispatch extinguisher", False, "Invalid response message")
        else:
            log_test("dispatch_functionality", "Dispatch extinguisher", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("dispatch_functionality", "Dispatch extinguisher", False, str(e))

    # Test 2: Get dispatched extinguishers
    try:
        response = requests.get(f"{API_URL}/fire-extinguishers/dispatched")
        if response.status_code == 200:
            dispatched_extinguishers = response.json()
            if isinstance(dispatched_extinguishers, list) and len(dispatched_extinguishers) > 0:
                # Check if our extinguisher is in the list
                found_extinguisher = next((ext for ext in dispatched_extinguishers if ext["id"] == extinguisher_id), None)
                if found_extinguisher and found_extinguisher["dispatch_status"] == "dispatched":
                    log_test("dispatch_functionality", "Get dispatched extinguishers", True)
                else:
                    log_test("dispatch_functionality", "Get dispatched extinguishers", False, "Dispatched extinguisher not found in list")
            else:
                log_test("dispatch_functionality", "Get dispatched extinguishers", False, "No dispatched extinguishers found")
        else:
            log_test("dispatch_functionality", "Get dispatched extinguishers", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("dispatch_functionality", "Get dispatched extinguishers", False, str(e))

    # Test 3: Update dispatch status to "under_process"
    try:
        response = requests.put(f"{API_URL}/fire-extinguishers/{extinguisher_id}/dispatch-status", 
                               json="under_process", 
                               headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            result = response.json()
            if "message" in result and "updated successfully" in result["message"]:
                log_test("dispatch_functionality", "Update dispatch status to under_process", True)
                
                # Verify status was updated
                ext_response = requests.get(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
                if ext_response.status_code == 200:
                    ext_data = ext_response.json()
                    if ext_data["dispatch_status"] == "under_process":
                        log_test("dispatch_functionality", "Verify dispatch status update to under_process", True)
                    else:
                        log_test("dispatch_functionality", "Verify dispatch status update to under_process", False, f"Status: {ext_data['dispatch_status']}")
                else:
                    log_test("dispatch_functionality", "Verify dispatch status update to under_process", False, "Could not fetch extinguisher")
            else:
                log_test("dispatch_functionality", "Update dispatch status to under_process", False, "Invalid response message")
        else:
            log_test("dispatch_functionality", "Update dispatch status to under_process", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("dispatch_functionality", "Update dispatch status to under_process", False, str(e))

    # Test 4: Mark as received (should update refill date)
    try:
        response = requests.post(f"{API_URL}/fire-extinguishers/{extinguisher_id}/receive")
        if response.status_code == 200:
            result = response.json()
            if "message" in result and "received" in result["message"] and "refill date updated" in result["message"]:
                log_test("dispatch_functionality", "Mark extinguisher as received", True)
                
                # Verify status and refill date were updated
                ext_response = requests.get(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
                if ext_response.status_code == 200:
                    ext_data = ext_response.json()
                    if (ext_data["dispatch_status"] == "received" and 
                        ext_data["received_date"] and 
                        ext_data["status"] == "active"):
                        log_test("dispatch_functionality", "Verify received status and refill date update", True)
                    else:
                        log_test("dispatch_functionality", "Verify received status and refill date update", False, 
                               f"Status: {ext_data['dispatch_status']}, Received date: {ext_data.get('received_date')}, Extinguisher status: {ext_data['status']}")
                else:
                    log_test("dispatch_functionality", "Verify received status and refill date update", False, "Could not fetch extinguisher")
            else:
                log_test("dispatch_functionality", "Mark extinguisher as received", False, "Invalid response message")
        else:
            log_test("dispatch_functionality", "Mark extinguisher as received", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("dispatch_functionality", "Mark extinguisher as received", False, str(e))

    # Test 5: Verify dispatch status tracking workflow
    try:
        # Create another extinguisher to test full workflow
        create_data2 = {
            "name": "Workflow Test Extinguisher",
            "location": "Workflow Test Area",
            "last_refill": (now - timedelta(days=30)).isoformat(),
            "last_pressure_test": (now - timedelta(days=60)).isoformat()
        }
        response = requests.post(f"{API_URL}/fire-extinguishers", json=create_data2)
        if response.status_code == 200:
            extinguisher2 = response.json()
            extinguisher2_id = extinguisher2["id"]
            
            # Test workflow: none -> dispatched -> under_process -> received
            workflow_steps = [
                ("dispatched", f"{API_URL}/fire-extinguishers/{extinguisher2_id}/dispatch", "POST"),
                ("under_process", f"{API_URL}/fire-extinguishers/{extinguisher2_id}/dispatch-status", "PUT"),
                ("received", f"{API_URL}/fire-extinguishers/{extinguisher2_id}/receive", "POST")
            ]
            
            workflow_success = True
            for expected_status, url, method in workflow_steps:
                if method == "POST":
                    if "dispatch-status" in url:
                        continue  # Skip this step for POST
                    step_response = requests.post(url)
                elif method == "PUT":
                    step_response = requests.put(url, json=expected_status, headers={"Content-Type": "application/json"})
                
                if step_response.status_code != 200:
                    workflow_success = False
                    break
                
                # Verify status
                verify_response = requests.get(f"{API_URL}/fire-extinguishers/{extinguisher2_id}")
                if verify_response.status_code == 200:
                    ext_data = verify_response.json()
                    if ext_data["dispatch_status"] != expected_status:
                        workflow_success = False
                        break
                else:
                    workflow_success = False
                    break
            
            if workflow_success:
                log_test("dispatch_functionality", "Complete dispatch workflow tracking", True)
            else:
                log_test("dispatch_functionality", "Complete dispatch workflow tracking", False, "Workflow step failed")
            
            # Cleanup second extinguisher
            requests.delete(f"{API_URL}/fire-extinguishers/{extinguisher2_id}")
        else:
            log_test("dispatch_functionality", "Complete dispatch workflow tracking", False, "Could not create second test extinguisher")
    except Exception as e:
        log_test("dispatch_functionality", "Complete dispatch workflow tracking", False, str(e))

    # Test 6: Test dispatch status values validation
    try:
        # Test invalid dispatch status
        response = requests.put(f"{API_URL}/fire-extinguishers/{extinguisher_id}/dispatch-status", 
                               json="invalid_status", 
                               headers={"Content-Type": "application/json"})
        if response.status_code == 422:  # Validation error expected
            log_test("dispatch_functionality", "Validate dispatch status enum values", True)
        else:
            log_test("dispatch_functionality", "Validate dispatch status enum values", False, f"Expected 422, got {response.status_code}")
    except Exception as e:
        log_test("dispatch_functionality", "Validate dispatch status enum values", False, str(e))

    # Cleanup test extinguisher
    try:
        requests.delete(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
    except:
        pass

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("BACKEND API TEST SUMMARY")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    
    for category, results in test_results.items():
        passed = results["passed"]
        failed = results["failed"]
        total_passed += passed
        total_failed += failed
        
        status = "✅ PASS" if failed == 0 else "❌ FAIL"
        print(f"{category.replace('_', ' ').title()}: {status} ({passed} passed, {failed} failed)")
        
        if results["errors"]:
            for error in results["errors"]:
                print(f"  - {error}")
    
    print(f"\nOVERALL: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 ALL BACKEND TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME BACKEND TESTS FAILED!")
        return False

def main():
    """Run all backend tests"""
    print("Starting Fire Safety Management System Backend API Tests")
    print(f"Testing against: {API_URL}")
    print("="*60)
    
    # Run all test suites
    test_smoke_detector_crud()
    test_fire_extinguisher_crud()
    test_smoke_detector_trigger_system()
    test_alert_management()
    test_dashboard_api()
    
    # Print summary
    success = print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)