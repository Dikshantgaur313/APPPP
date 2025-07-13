#!/usr/bin/env python3
"""
Admin Authentication Testing for Fire Safety Management System
Tests admin login, verification, and protected CRUD operations
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys
import base64

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
print(f"Testing Admin Authentication API at: {API_URL}")

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "firesafety2025"

# Test results tracking
test_results = {
    "admin_authentication": {"passed": 0, "failed": 0, "errors": []},
    "admin_smoke_detector_crud": {"passed": 0, "failed": 0, "errors": []},
    "admin_fire_extinguisher_crud": {"passed": 0, "failed": 0, "errors": []},
    "public_endpoints": {"passed": 0, "failed": 0, "errors": []},
    "security_testing": {"passed": 0, "failed": 0, "errors": []}
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

def get_basic_auth_header(username, password):
    """Create basic auth header"""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}

def test_admin_authentication():
    """Test Admin Authentication Endpoints"""
    print("\n=== Testing Admin Authentication ===")
    
    # Test LOGIN with valid credentials
    try:
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{API_URL}/admin/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("admin") == True and "message" in result:
                log_test("admin_authentication", "Admin login with valid credentials", True)
            else:
                log_test("admin_authentication", "Admin login with valid credentials", False, "Invalid response structure")
        else:
            log_test("admin_authentication", "Admin login with valid credentials", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("admin_authentication", "Admin login with valid credentials", False, str(e))

    # Test LOGIN with invalid credentials
    try:
        login_data = {
            "username": "wronguser",
            "password": "wrongpass"
        }
        response = requests.post(f"{API_URL}/admin/login", json=login_data)
        if response.status_code == 401:
            log_test("admin_authentication", "Admin login with invalid credentials (should fail)", True)
        else:
            log_test("admin_authentication", "Admin login with invalid credentials (should fail)", False, f"Expected 401, got {response.status_code}")
    except Exception as e:
        log_test("admin_authentication", "Admin login with invalid credentials (should fail)", False, str(e))

    # Test VERIFY with proper basic auth
    try:
        headers = get_basic_auth_header(ADMIN_USERNAME, ADMIN_PASSWORD)
        response = requests.get(f"{API_URL}/admin/verify", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if "admin" in result and result["admin"] == ADMIN_USERNAME:
                log_test("admin_authentication", "Admin verify with proper basic auth", True)
            else:
                log_test("admin_authentication", "Admin verify with proper basic auth", False, "Invalid response structure")
        else:
            log_test("admin_authentication", "Admin verify with proper basic auth", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("admin_authentication", "Admin verify with proper basic auth", False, str(e))

    # Test VERIFY with invalid basic auth
    try:
        headers = get_basic_auth_header("wronguser", "wrongpass")
        response = requests.get(f"{API_URL}/admin/verify", headers=headers)
        if response.status_code == 401:
            log_test("admin_authentication", "Admin verify with invalid basic auth (should fail)", True)
        else:
            log_test("admin_authentication", "Admin verify with invalid basic auth (should fail)", False, f"Expected 401, got {response.status_code}")
    except Exception as e:
        log_test("admin_authentication", "Admin verify with invalid basic auth (should fail)", False, str(e))

def test_admin_smoke_detector_crud():
    """Test Admin-only Smoke Detector CRUD Operations"""
    print("\n=== Testing Admin Smoke Detector CRUD Operations ===")
    
    auth_headers = get_basic_auth_header(ADMIN_USERNAME, ADMIN_PASSWORD)
    detector_id = None
    
    # Test CREATE with admin auth
    try:
        create_data = {
            "name": "Admin Test Smoke Detector",
            "location": "Admin Test Area",
            "battery_level": 85
        }
        response = requests.post(f"{API_URL}/admin/smoke-detectors", json=create_data, headers=auth_headers)
        if response.status_code == 200:
            detector = response.json()
            detector_id = detector["id"]
            if detector["name"] == create_data["name"] and detector["location"] == create_data["location"]:
                log_test("admin_smoke_detector_crud", "Create smoke detector with admin auth", True)
            else:
                log_test("admin_smoke_detector_crud", "Create smoke detector with admin auth", False, "Data mismatch")
        else:
            log_test("admin_smoke_detector_crud", "Create smoke detector with admin auth", False, f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("admin_smoke_detector_crud", "Create smoke detector with admin auth", False, str(e))
        return

    # Test CREATE without admin auth (should fail)
    try:
        create_data = {
            "name": "Unauthorized Test Detector",
            "location": "Unauthorized Area",
            "battery_level": 90
        }
        response = requests.post(f"{API_URL}/admin/smoke-detectors", json=create_data)
        if response.status_code == 401:
            log_test("admin_smoke_detector_crud", "Create smoke detector without auth (should fail)", True)
        else:
            log_test("admin_smoke_detector_crud", "Create smoke detector without auth (should fail)", False, f"Expected 401, got {response.status_code}")
    except Exception as e:
        log_test("admin_smoke_detector_crud", "Create smoke detector without auth (should fail)", False, str(e))

    # Test UPDATE with admin auth
    try:
        update_data = {
            "name": "Updated Admin Test Detector",
            "battery_level": 75
        }
        response = requests.put(f"{API_URL}/admin/smoke-detectors/{detector_id}", json=update_data, headers=auth_headers)
        if response.status_code == 200:
            updated_detector = response.json()
            if updated_detector["name"] == "Updated Admin Test Detector" and updated_detector["battery_level"] == 75:
                log_test("admin_smoke_detector_crud", "Update smoke detector with admin auth", True)
            else:
                log_test("admin_smoke_detector_crud", "Update smoke detector with admin auth", False, "Update not reflected")
        else:
            log_test("admin_smoke_detector_crud", "Update smoke detector with admin auth", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("admin_smoke_detector_crud", "Update smoke detector with admin auth", False, str(e))

    # Test UPDATE without admin auth (should fail)
    try:
        update_data = {
            "name": "Unauthorized Update",
            "battery_level": 50
        }
        response = requests.put(f"{API_URL}/admin/smoke-detectors/{detector_id}", json=update_data)
        if response.status_code == 401:
            log_test("admin_smoke_detector_crud", "Update smoke detector without auth (should fail)", True)
        else:
            log_test("admin_smoke_detector_crud", "Update smoke detector without auth (should fail)", False, f"Expected 401, got {response.status_code}")
    except Exception as e:
        log_test("admin_smoke_detector_crud", "Update smoke detector without auth (should fail)", False, str(e))

    # Test DELETE with admin auth
    try:
        response = requests.delete(f"{API_URL}/admin/smoke-detectors/{detector_id}", headers=auth_headers)
        if response.status_code == 200:
            # Verify deletion by trying to get the detector
            verify_response = requests.get(f"{API_URL}/smoke-detectors/{detector_id}")
            if verify_response.status_code == 404:
                log_test("admin_smoke_detector_crud", "Delete smoke detector with admin auth", True)
            else:
                log_test("admin_smoke_detector_crud", "Delete smoke detector with admin auth", False, "Detector still exists after deletion")
        else:
            log_test("admin_smoke_detector_crud", "Delete smoke detector with admin auth", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("admin_smoke_detector_crud", "Delete smoke detector with admin auth", False, str(e))

    # Test DELETE without admin auth (should fail) - create another detector first
    try:
        create_data = {
            "name": "Delete Test Detector",
            "location": "Delete Test Area",
            "battery_level": 80
        }
        create_response = requests.post(f"{API_URL}/admin/smoke-detectors", json=create_data, headers=auth_headers)
        if create_response.status_code == 200:
            test_detector_id = create_response.json()["id"]
            
            # Try to delete without auth
            response = requests.delete(f"{API_URL}/admin/smoke-detectors/{test_detector_id}")
            if response.status_code == 401:
                log_test("admin_smoke_detector_crud", "Delete smoke detector without auth (should fail)", True)
            else:
                log_test("admin_smoke_detector_crud", "Delete smoke detector without auth (should fail)", False, f"Expected 401, got {response.status_code}")
            
            # Cleanup - delete with proper auth
            requests.delete(f"{API_URL}/admin/smoke-detectors/{test_detector_id}", headers=auth_headers)
        else:
            log_test("admin_smoke_detector_crud", "Delete smoke detector without auth (should fail)", False, "Could not create test detector")
    except Exception as e:
        log_test("admin_smoke_detector_crud", "Delete smoke detector without auth (should fail)", False, str(e))

def test_admin_fire_extinguisher_crud():
    """Test Admin-only Fire Extinguisher CRUD Operations"""
    print("\n=== Testing Admin Fire Extinguisher CRUD Operations ===")
    
    auth_headers = get_basic_auth_header(ADMIN_USERNAME, ADMIN_PASSWORD)
    extinguisher_id = None
    
    # Test CREATE with admin auth
    try:
        now = datetime.utcnow()
        create_data = {
            "name": "Admin Test Fire Extinguisher",
            "location": "Admin Test Area",
            "last_refill": (now - timedelta(days=30)).isoformat(),
            "last_pressure_test": (now - timedelta(days=60)).isoformat()
        }
        response = requests.post(f"{API_URL}/admin/fire-extinguishers", json=create_data, headers=auth_headers)
        if response.status_code == 200:
            extinguisher = response.json()
            extinguisher_id = extinguisher["id"]
            if (extinguisher["name"] == create_data["name"] and 
                extinguisher["location"] == create_data["location"] and
                "next_refill_due" in extinguisher and 
                "next_pressure_test_due" in extinguisher):
                log_test("admin_fire_extinguisher_crud", "Create fire extinguisher with admin auth", True)
            else:
                log_test("admin_fire_extinguisher_crud", "Create fire extinguisher with admin auth", False, "Data mismatch or missing due dates")
        else:
            log_test("admin_fire_extinguisher_crud", "Create fire extinguisher with admin auth", False, f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("admin_fire_extinguisher_crud", "Create fire extinguisher with admin auth", False, str(e))
        return

    # Test CREATE without admin auth (should fail)
    try:
        now = datetime.utcnow()
        create_data = {
            "name": "Unauthorized Test Extinguisher",
            "location": "Unauthorized Area",
            "last_refill": (now - timedelta(days=30)).isoformat(),
            "last_pressure_test": (now - timedelta(days=60)).isoformat()
        }
        response = requests.post(f"{API_URL}/admin/fire-extinguishers", json=create_data)
        if response.status_code == 401:
            log_test("admin_fire_extinguisher_crud", "Create fire extinguisher without auth (should fail)", True)
        else:
            log_test("admin_fire_extinguisher_crud", "Create fire extinguisher without auth (should fail)", False, f"Expected 401, got {response.status_code}")
    except Exception as e:
        log_test("admin_fire_extinguisher_crud", "Create fire extinguisher without auth (should fail)", False, str(e))

    # Test UPDATE with admin auth
    try:
        new_refill_date = datetime.utcnow() - timedelta(days=10)
        update_data = {
            "name": "Updated Admin Test Extinguisher",
            "last_refill": new_refill_date.isoformat()
        }
        response = requests.put(f"{API_URL}/admin/fire-extinguishers/{extinguisher_id}", json=update_data, headers=auth_headers)
        if response.status_code == 200:
            updated_extinguisher = response.json()
            if updated_extinguisher["name"] == "Updated Admin Test Extinguisher":
                log_test("admin_fire_extinguisher_crud", "Update fire extinguisher with admin auth", True)
            else:
                log_test("admin_fire_extinguisher_crud", "Update fire extinguisher with admin auth", False, "Update not reflected")
        else:
            log_test("admin_fire_extinguisher_crud", "Update fire extinguisher with admin auth", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("admin_fire_extinguisher_crud", "Update fire extinguisher with admin auth", False, str(e))

    # Test UPDATE without admin auth (should fail)
    try:
        update_data = {
            "name": "Unauthorized Update",
        }
        response = requests.put(f"{API_URL}/admin/fire-extinguishers/{extinguisher_id}", json=update_data)
        if response.status_code == 401:
            log_test("admin_fire_extinguisher_crud", "Update fire extinguisher without auth (should fail)", True)
        else:
            log_test("admin_fire_extinguisher_crud", "Update fire extinguisher without auth (should fail)", False, f"Expected 401, got {response.status_code}")
    except Exception as e:
        log_test("admin_fire_extinguisher_crud", "Update fire extinguisher without auth (should fail)", False, str(e))

    # Test DELETE with admin auth
    try:
        response = requests.delete(f"{API_URL}/admin/fire-extinguishers/{extinguisher_id}", headers=auth_headers)
        if response.status_code == 200:
            # Verify deletion by trying to get the extinguisher
            verify_response = requests.get(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
            if verify_response.status_code == 404:
                log_test("admin_fire_extinguisher_crud", "Delete fire extinguisher with admin auth", True)
            else:
                log_test("admin_fire_extinguisher_crud", "Delete fire extinguisher with admin auth", False, "Extinguisher still exists after deletion")
        else:
            log_test("admin_fire_extinguisher_crud", "Delete fire extinguisher with admin auth", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("admin_fire_extinguisher_crud", "Delete fire extinguisher with admin auth", False, str(e))

    # Test DELETE without admin auth (should fail) - create another extinguisher first
    try:
        now = datetime.utcnow()
        create_data = {
            "name": "Delete Test Extinguisher",
            "location": "Delete Test Area",
            "last_refill": (now - timedelta(days=30)).isoformat(),
            "last_pressure_test": (now - timedelta(days=60)).isoformat()
        }
        create_response = requests.post(f"{API_URL}/admin/fire-extinguishers", json=create_data, headers=auth_headers)
        if create_response.status_code == 200:
            test_extinguisher_id = create_response.json()["id"]
            
            # Try to delete without auth
            response = requests.delete(f"{API_URL}/admin/fire-extinguishers/{test_extinguisher_id}")
            if response.status_code == 401:
                log_test("admin_fire_extinguisher_crud", "Delete fire extinguisher without auth (should fail)", True)
            else:
                log_test("admin_fire_extinguisher_crud", "Delete fire extinguisher without auth (should fail)", False, f"Expected 401, got {response.status_code}")
            
            # Cleanup - delete with proper auth
            requests.delete(f"{API_URL}/admin/fire-extinguishers/{test_extinguisher_id}", headers=auth_headers)
        else:
            log_test("admin_fire_extinguisher_crud", "Delete fire extinguisher without auth (should fail)", False, "Could not create test extinguisher")
    except Exception as e:
        log_test("admin_fire_extinguisher_crud", "Delete fire extinguisher without auth (should fail)", False, str(e))

def test_public_endpoints():
    """Test that public endpoints work without authentication"""
    print("\n=== Testing Public Endpoints (No Auth Required) ===")
    
    auth_headers = get_basic_auth_header(ADMIN_USERNAME, ADMIN_PASSWORD)
    
    # Create test data first using admin endpoints
    detector_id = None
    extinguisher_id = None
    
    try:
        # Create test detector
        create_data = {
            "name": "Public Test Smoke Detector",
            "location": "Public Test Area",
            "battery_level": 85
        }
        response = requests.post(f"{API_URL}/admin/smoke-detectors", json=create_data, headers=auth_headers)
        if response.status_code == 200:
            detector_id = response.json()["id"]
        
        # Create test extinguisher
        now = datetime.utcnow()
        create_data = {
            "name": "Public Test Fire Extinguisher",
            "location": "Public Test Area",
            "last_refill": (now - timedelta(days=30)).isoformat(),
            "last_pressure_test": (now - timedelta(days=60)).isoformat()
        }
        response = requests.post(f"{API_URL}/admin/fire-extinguishers", json=create_data, headers=auth_headers)
        if response.status_code == 200:
            extinguisher_id = response.json()["id"]
    except Exception as e:
        print(f"Warning: Could not create test data: {e}")

    # Test public smoke detector endpoints
    try:
        response = requests.get(f"{API_URL}/smoke-detectors")
        if response.status_code == 200:
            detectors = response.json()
            if isinstance(detectors, list):
                log_test("public_endpoints", "Get all smoke detectors (public)", True)
            else:
                log_test("public_endpoints", "Get all smoke detectors (public)", False, "Invalid response format")
        else:
            log_test("public_endpoints", "Get all smoke detectors (public)", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("public_endpoints", "Get all smoke detectors (public)", False, str(e))

    if detector_id:
        try:
            response = requests.get(f"{API_URL}/smoke-detectors/{detector_id}")
            if response.status_code == 200:
                detector = response.json()
                if detector["id"] == detector_id:
                    log_test("public_endpoints", "Get single smoke detector (public)", True)
                else:
                    log_test("public_endpoints", "Get single smoke detector (public)", False, "ID mismatch")
            else:
                log_test("public_endpoints", "Get single smoke detector (public)", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("public_endpoints", "Get single smoke detector (public)", False, str(e))

        # Test trigger endpoint (public)
        try:
            response = requests.post(f"{API_URL}/smoke-detectors/{detector_id}/trigger")
            if response.status_code == 200:
                result = response.json()
                if "alert_id" in result:
                    log_test("public_endpoints", "Trigger smoke detector (public)", True)
                else:
                    log_test("public_endpoints", "Trigger smoke detector (public)", False, "No alert_id returned")
            else:
                log_test("public_endpoints", "Trigger smoke detector (public)", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("public_endpoints", "Trigger smoke detector (public)", False, str(e))

        # Test reset endpoint (public)
        try:
            response = requests.post(f"{API_URL}/smoke-detectors/{detector_id}/reset")
            if response.status_code == 200:
                log_test("public_endpoints", "Reset smoke detector (public)", True)
            else:
                log_test("public_endpoints", "Reset smoke detector (public)", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("public_endpoints", "Reset smoke detector (public)", False, str(e))

    # Test public fire extinguisher endpoints
    try:
        response = requests.get(f"{API_URL}/fire-extinguishers")
        if response.status_code == 200:
            extinguishers = response.json()
            if isinstance(extinguishers, list):
                log_test("public_endpoints", "Get all fire extinguishers (public)", True)
            else:
                log_test("public_endpoints", "Get all fire extinguishers (public)", False, "Invalid response format")
        else:
            log_test("public_endpoints", "Get all fire extinguishers (public)", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("public_endpoints", "Get all fire extinguishers (public)", False, str(e))

    if extinguisher_id:
        try:
            response = requests.get(f"{API_URL}/fire-extinguishers/{extinguisher_id}")
            if response.status_code == 200:
                extinguisher = response.json()
                if extinguisher["id"] == extinguisher_id:
                    log_test("public_endpoints", "Get single fire extinguisher (public)", True)
                else:
                    log_test("public_endpoints", "Get single fire extinguisher (public)", False, "ID mismatch")
            else:
                log_test("public_endpoints", "Get single fire extinguisher (public)", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("public_endpoints", "Get single fire extinguisher (public)", False, str(e))

    # Cleanup test data
    try:
        if detector_id:
            requests.delete(f"{API_URL}/admin/smoke-detectors/{detector_id}", headers=auth_headers)
        if extinguisher_id:
            requests.delete(f"{API_URL}/admin/fire-extinguishers/{extinguisher_id}", headers=auth_headers)
    except:
        pass

def test_security():
    """Test security aspects of admin endpoints"""
    print("\n=== Testing Security ===")
    
    # Test admin endpoints with various invalid auth scenarios
    test_endpoints = [
        ("POST", "/admin/smoke-detectors", {"name": "Test", "location": "Test"}),
        ("PUT", "/admin/smoke-detectors/test-id", {"name": "Test"}),
        ("DELETE", "/admin/smoke-detectors/test-id", None),
        ("POST", "/admin/fire-extinguishers", {"name": "Test", "location": "Test", "last_refill": datetime.utcnow().isoformat(), "last_pressure_test": datetime.utcnow().isoformat()}),
        ("PUT", "/admin/fire-extinguishers/test-id", {"name": "Test"}),
        ("DELETE", "/admin/fire-extinguishers/test-id", None)
    ]
    
    for method, endpoint, data in test_endpoints:
        try:
            # Test with no auth header
            if method == "POST":
                response = requests.post(f"{API_URL}{endpoint}", json=data)
            elif method == "PUT":
                response = requests.put(f"{API_URL}{endpoint}", json=data)
            elif method == "DELETE":
                response = requests.delete(f"{API_URL}{endpoint}")
            
            if response.status_code == 401:
                log_test("security_testing", f"{method} {endpoint} without auth (should fail)", True)
            else:
                log_test("security_testing", f"{method} {endpoint} without auth (should fail)", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            log_test("security_testing", f"{method} {endpoint} without auth (should fail)", False, str(e))

        try:
            # Test with invalid auth header
            invalid_headers = get_basic_auth_header("invalid", "credentials")
            if method == "POST":
                response = requests.post(f"{API_URL}{endpoint}", json=data, headers=invalid_headers)
            elif method == "PUT":
                response = requests.put(f"{API_URL}{endpoint}", json=data, headers=invalid_headers)
            elif method == "DELETE":
                response = requests.delete(f"{API_URL}{endpoint}", headers=invalid_headers)
            
            if response.status_code == 401:
                log_test("security_testing", f"{method} {endpoint} with invalid auth (should fail)", True)
            else:
                log_test("security_testing", f"{method} {endpoint} with invalid auth (should fail)", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            log_test("security_testing", f"{method} {endpoint} with invalid auth (should fail)", False, str(e))

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("ADMIN AUTHENTICATION TEST SUMMARY")
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
        print("🎉 ALL ADMIN AUTHENTICATION TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME ADMIN AUTHENTICATION TESTS FAILED!")
        return False

def main():
    """Run all admin authentication tests"""
    print("Starting Fire Safety Management System Admin Authentication Tests")
    print(f"Testing against: {API_URL}")
    print("="*60)
    
    # Run all test suites
    test_admin_authentication()
    test_admin_smoke_detector_crud()
    test_admin_fire_extinguisher_crud()
    test_public_endpoints()
    test_security()
    
    # Print summary
    success = print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)