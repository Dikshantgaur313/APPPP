#!/usr/bin/env python3
"""
Focused Test for Fire Extinguisher Dispatch Functionality
Tests the new dispatch endpoints that were just added
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
print(f"Testing Dispatch API at: {API_URL}")

# Test results tracking
test_results = {
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

def test_dispatch_functionality():
    """Test Fire Extinguisher Dispatch Functionality"""
    print("\n=== Testing Fire Extinguisher Dispatch Functionality ===")
    
    # First get existing extinguishers to get an ID
    try:
        response = requests.get(f"{API_URL}/fire-extinguishers")
        if response.status_code == 200:
            extinguishers = response.json()
            if isinstance(extinguishers, list) and len(extinguishers) > 0:
                # Find an extinguisher with dispatch_status "none" to test with
                test_extinguisher = None
                for ext in extinguishers:
                    if ext["dispatch_status"] == "none":
                        test_extinguisher = ext
                        break
                
                if test_extinguisher:
                    extinguisher_id = test_extinguisher["id"]
                    log_test("dispatch_functionality", "Get existing extinguisher for testing", True)
                else:
                    # Use the first extinguisher anyway for testing
                    extinguisher_id = extinguishers[0]["id"]
                    log_test("dispatch_functionality", "Get existing extinguisher for testing", True)
            else:
                log_test("dispatch_functionality", "Get existing extinguisher for testing", False, "No extinguishers found")
                return
        else:
            log_test("dispatch_functionality", "Get existing extinguisher for testing", False, f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("dispatch_functionality", "Get existing extinguisher for testing", False, str(e))
        return

    print(f"Using extinguisher ID: {extinguisher_id}")

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
                if found_extinguisher and found_extinguisher["dispatch_status"] in ["dispatched", "under_process", "received"]:
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

    # Test 5: Test complete workflow with another extinguisher
    try:
        # Get another extinguisher for workflow testing
        response = requests.get(f"{API_URL}/fire-extinguishers")
        if response.status_code == 200:
            extinguishers = response.json()
            workflow_extinguisher = None
            for ext in extinguishers:
                if ext["id"] != extinguisher_id and ext["dispatch_status"] == "none":
                    workflow_extinguisher = ext
                    break
            
            if workflow_extinguisher:
                extinguisher2_id = workflow_extinguisher["id"]
                
                # Test workflow: none -> dispatched -> under_process -> received
                workflow_steps = [
                    ("dispatched", f"{API_URL}/fire-extinguishers/{extinguisher2_id}/dispatch", "POST"),
                    ("under_process", f"{API_URL}/fire-extinguishers/{extinguisher2_id}/dispatch-status", "PUT"),
                    ("received", f"{API_URL}/fire-extinguishers/{extinguisher2_id}/receive", "POST")
                ]
                
                workflow_success = True
                for expected_status, url, method in workflow_steps:
                    if method == "POST":
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
            else:
                log_test("dispatch_functionality", "Complete dispatch workflow tracking", False, "No available extinguisher for workflow test")
        else:
            log_test("dispatch_functionality", "Complete dispatch workflow tracking", False, "Could not get extinguishers for workflow test")
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

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("DISPATCH FUNCTIONALITY TEST SUMMARY")
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
        print("🎉 ALL DISPATCH TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME DISPATCH TESTS FAILED!")
        return False

def main():
    """Run dispatch functionality tests"""
    print("Starting Fire Extinguisher Dispatch Functionality Tests")
    print(f"Testing against: {API_URL}")
    print("="*60)
    
    # Run dispatch tests
    test_dispatch_functionality()
    
    # Print summary
    success = print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)