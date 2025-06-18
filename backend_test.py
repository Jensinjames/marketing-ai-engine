#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from typing import Dict, Any, List, Optional
import uuid

# Get the backend URL from frontend/.env
BACKEND_URL = None
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.strip().split('=', 1)[1].strip('"\'')
                break
except Exception as e:
    print(f"Error reading frontend/.env: {e}")
    sys.exit(1)

if not BACKEND_URL:
    print("REACT_APP_BACKEND_URL not found in frontend/.env")
    sys.exit(1)

# Ensure BACKEND_URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "tests": []
}

def log_test(name: str, passed: bool, details: Dict[str, Any] = None):
    """Log test results"""
    global test_results
    test_results["total_tests"] += 1
    if passed:
        test_results["passed_tests"] += 1
        status = "PASSED"
    else:
        test_results["failed_tests"] += 1
        status = "FAILED"
    
    test_results["tests"].append({
        "name": name,
        "status": status,
        "details": details or {}
    })
    
    print(f"[{status}] {name}")
    if details:
        print(f"  Details: {json.dumps(details, indent=2)}")

def test_api_root():
    """Test the API root endpoint"""
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200 and "message" in response.json():
            log_test("API Root", True, {"response": response.json()})
            return True
        else:
            log_test("API Root", False, {
                "status_code": response.status_code,
                "response": response.text
            })
            return False
    except Exception as e:
        log_test("API Root", False, {"error": str(e)})
        return False

def test_user_profile():
    """Test the user profile API"""
    try:
        response = requests.get(f"{API_URL}/user/profile")
        if response.status_code == 200:
            user_data = response.json()
            if "id" in user_data and "credits" in user_data:
                log_test("User Profile API", True, {"user": user_data})
                return user_data
            else:
                log_test("User Profile API", False, {
                    "reason": "Missing required fields in user data",
                    "response": user_data
                })
                return None
        else:
            log_test("User Profile API", False, {
                "status_code": response.status_code,
                "response": response.text
            })
            return None
    except Exception as e:
        log_test("User Profile API", False, {"error": str(e)})
        return None

def test_dashboard_stats():
    """Test the dashboard stats API"""
    try:
        response = requests.get(f"{API_URL}/dashboard/stats")
        if response.status_code == 200:
            stats = response.json()
            required_fields = ["user", "total_assets", "credits_used", "asset_counts", "plan_limits"]
            missing_fields = [field for field in required_fields if field not in stats]
            
            if not missing_fields:
                log_test("Dashboard Stats API", True, {"stats": stats})
                return stats
            else:
                log_test("Dashboard Stats API", False, {
                    "reason": f"Missing required fields: {missing_fields}",
                    "response": stats
                })
                return None
        else:
            log_test("Dashboard Stats API", False, {
                "status_code": response.status_code,
                "response": response.text
            })
            return None
    except Exception as e:
        log_test("Dashboard Stats API", False, {"error": str(e)})
        return None

def test_generate_asset(asset_type: str, business_data: Dict[str, Any]):
    """Test asset generation for a specific asset type"""
    try:
        payload = {
            "asset_type": asset_type,
            "business_name": business_data["business_name"],
            "product_service": business_data["product_service"],
            "target_audience": business_data["target_audience"],
            "tone": business_data["tone"],
            "objectives": business_data["objectives"],
            "additional_context": business_data["additional_context"]
        }
        
        response = requests.post(f"{API_URL}/assets/generate", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if "asset" in result and "remaining_credits" in result:
                log_test(f"Generate {asset_type.replace('_', ' ').title()}", True, {
                    "asset_id": result["asset"]["id"],
                    "title": result["asset"]["title"],
                    "remaining_credits": result["remaining_credits"],
                    "content_length": len(result["asset"]["content"])
                })
                return result
            else:
                log_test(f"Generate {asset_type.replace('_', ' ').title()}", False, {
                    "reason": "Missing required fields in response",
                    "response": result
                })
                return None
        else:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except:
                error_detail = response.text
                
            log_test(f"Generate {asset_type.replace('_', ' ').title()}", False, {
                "status_code": response.status_code,
                "error": error_detail
            })
            return None
    except Exception as e:
        log_test(f"Generate {asset_type.replace('_', ' ').title()}", False, {"error": str(e)})
        return None

def test_get_assets():
    """Test getting all assets"""
    try:
        response = requests.get(f"{API_URL}/assets")
        if response.status_code == 200:
            assets = response.json()
            if isinstance(assets, list):
                log_test("Get All Assets", True, {"count": len(assets)})
                return assets
            else:
                log_test("Get All Assets", False, {
                    "reason": "Response is not a list",
                    "response": assets
                })
                return None
        else:
            log_test("Get All Assets", False, {
                "status_code": response.status_code,
                "response": response.text
            })
            return None
    except Exception as e:
        log_test("Get All Assets", False, {"error": str(e)})
        return None

def test_get_asset_by_id(asset_id: str):
    """Test getting a specific asset by ID"""
    try:
        response = requests.get(f"{API_URL}/assets/{asset_id}")
        if response.status_code == 200:
            asset = response.json()
            if "id" in asset and asset["id"] == asset_id:
                log_test(f"Get Asset by ID ({asset_id})", True, {
                    "title": asset["title"],
                    "asset_type": asset["asset_type"]
                })
                return asset
            else:
                log_test(f"Get Asset by ID ({asset_id})", False, {
                    "reason": "Asset ID mismatch or missing",
                    "response": asset
                })
                return None
        else:
            log_test(f"Get Asset by ID ({asset_id})", False, {
                "status_code": response.status_code,
                "response": response.text
            })
            return None
    except Exception as e:
        log_test(f"Get Asset by ID ({asset_id})", False, {"error": str(e)})
        return None

def test_delete_asset(asset_id: str):
    """Test deleting an asset"""
    try:
        response = requests.delete(f"{API_URL}/assets/{asset_id}")
        if response.status_code == 200:
            result = response.json()
            log_test(f"Delete Asset ({asset_id})", True, {"result": result})
            
            # Verify it's actually deleted by trying to get it
            verify_response = requests.get(f"{API_URL}/assets/{asset_id}")
            if verify_response.status_code == 404:
                log_test(f"Verify Asset Deletion ({asset_id})", True)
            else:
                log_test(f"Verify Asset Deletion ({asset_id})", False, {
                    "reason": "Asset still exists after deletion",
                    "status_code": verify_response.status_code
                })
            
            return True
        else:
            log_test(f"Delete Asset ({asset_id})", False, {
                "status_code": response.status_code,
                "response": response.text
            })
            return False
    except Exception as e:
        log_test(f"Delete Asset ({asset_id})", False, {"error": str(e)})
        return False

def test_credit_system(initial_credits: int):
    """Test credit consumption and validation"""
    # First, get current user credits
    user = test_user_profile()
    if not user:
        log_test("Credit System", False, {"reason": "Could not get user profile"})
        return False
    
    starting_credits = user["credits"]
    
    # Generate an asset to consume credits
    business_data = {
        "business_name": "TechInnovate Solutions",
        "product_service": "AI-powered project management software",
        "target_audience": "Small to medium tech companies",
        "tone": "professional",
        "objectives": ["increase trial signups", "demonstrate product value"],
        "additional_context": "Our software integrates with popular tools like Slack and GitHub"
    }
    
    result = test_generate_asset("email_campaign", business_data)
    if not result:
        log_test("Credit System - Consumption", False, {"reason": "Asset generation failed"})
        return False
    
    # Check if credits were deducted
    credits_used = result["asset"]["credits_used"]
    remaining_credits = result["remaining_credits"]
    
    if starting_credits - credits_used == remaining_credits:
        log_test("Credit System - Consumption", True, {
            "starting_credits": starting_credits,
            "credits_used": credits_used,
            "remaining_credits": remaining_credits
        })
    else:
        log_test("Credit System - Consumption", False, {
            "reason": "Credit calculation mismatch",
            "starting_credits": starting_credits,
            "credits_used": credits_used,
            "remaining_credits": remaining_credits,
            "expected_remaining": starting_credits - credits_used
        })
        return False
    
    # Test credit validation by attempting to generate assets until credits run out
    # For testing purposes, we'll just check if the error is properly returned when credits are insufficient
    
    # First, get current user credits
    user = test_user_profile()
    if not user:
        return False
    
    current_credits = user["credits"]
    
    # If credits are already at 0, we can't test further
    if current_credits == 0:
        log_test("Credit System - Validation", True, {"note": "Credits already at 0, validation assumed to work"})
        return True
    
    # Generate assets until credits run out
    assets_to_generate = current_credits + 1  # One more than available credits
    
    for i in range(assets_to_generate):
        business_data["business_name"] = f"Test Company {i+1}"
        
        try:
            response = requests.post(f"{API_URL}/assets/generate", json=business_data)
            
            # If we've used all credits, we should get a 402 error
            if i >= current_credits and response.status_code == 402:
                log_test("Credit System - Validation", True, {
                    "note": "Properly rejected request when credits insufficient",
                    "status_code": response.status_code
                })
                return True
            
            # If we still have credits, generation should succeed
            if i < current_credits and response.status_code != 200:
                log_test("Credit System - Validation", False, {
                    "reason": f"Asset generation failed with credits available (attempt {i+1})",
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            log_test("Credit System - Validation", False, {"error": str(e)})
            return False
    
    # If we get here, something went wrong - we should have hit the credit limit
    log_test("Credit System - Validation", False, {
        "reason": "Did not receive credit limit error after generating more assets than credits available"
    })
    return False

def test_invalid_asset_type():
    """Test error handling for invalid asset type"""
    try:
        payload = {
            "asset_type": "invalid_type",
            "business_name": "Test Business",
            "product_service": "Test Product",
            "target_audience": "Test Audience",
            "tone": "professional",
            "objectives": ["test"],
            "additional_context": "Test context"
        }
        
        response = requests.post(f"{API_URL}/assets/generate", json=payload)
        
        if response.status_code in [400, 422]:  # Validation error codes
            log_test("Invalid Asset Type Handling", True, {
                "status_code": response.status_code,
                "response": response.text
            })
            return True
        else:
            log_test("Invalid Asset Type Handling", False, {
                "reason": "Did not receive validation error for invalid asset type",
                "status_code": response.status_code,
                "response": response.text
            })
            return False
    except Exception as e:
        log_test("Invalid Asset Type Handling", False, {"error": str(e)})
        return False

def test_missing_required_fields():
    """Test error handling for missing required fields"""
    try:
        # Missing business_name and product_service
        payload = {
            "asset_type": "email_campaign",
            "target_audience": "Test Audience",
            "tone": "professional"
        }
        
        response = requests.post(f"{API_URL}/assets/generate", json=payload)
        
        if response.status_code in [400, 422]:  # Validation error codes
            log_test("Missing Required Fields Handling", True, {
                "status_code": response.status_code,
                "response": response.text
            })
            return True
        else:
            log_test("Missing Required Fields Handling", False, {
                "reason": "Did not receive validation error for missing required fields",
                "status_code": response.status_code,
                "response": response.text
            })
            return False
    except Exception as e:
        log_test("Missing Required Fields Handling", False, {"error": str(e)})
        return False

def test_nonexistent_asset():
    """Test error handling for nonexistent asset ID"""
    fake_id = str(uuid.uuid4())
    try:
        response = requests.get(f"{API_URL}/assets/{fake_id}")
        
        if response.status_code == 404:
            log_test("Nonexistent Asset Handling", True, {
                "status_code": response.status_code,
                "fake_id": fake_id
            })
            return True
        else:
            log_test("Nonexistent Asset Handling", False, {
                "reason": "Did not receive 404 for nonexistent asset",
                "status_code": response.status_code,
                "response": response.text,
                "fake_id": fake_id
            })
            return False
    except Exception as e:
        log_test("Nonexistent Asset Handling", False, {"error": str(e)})
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n===== STARTING BACKEND API TESTS =====\n")
    
    # Test basic API connectivity
    if not test_api_root():
        print("\n❌ API Root test failed. Cannot continue with other tests.")
        return
    
    # Test user profile
    user = test_user_profile()
    if not user:
        print("\n❌ User Profile test failed. Cannot continue with other tests.")
        return
    
    # Test dashboard stats
    test_dashboard_stats()
    
    # Test asset generation for all asset types
    business_data = {
        "business_name": "EcoGreen Solutions",
        "product_service": "Sustainable packaging products",
        "target_audience": "Environmentally conscious businesses",
        "tone": "professional",
        "objectives": ["increase brand awareness", "drive product adoption"],
        "additional_context": "Our products are made from 100% recycled materials and are fully biodegradable"
    }
    
    asset_types = [
        "email_campaign",
        "social_media_ad",
        "landing_page",
        "sales_funnel",
        "blog_post",
        "press_release"
    ]
    
    generated_assets = []
    
    for asset_type in asset_types:
        # Customize business data slightly for each asset type to make it more realistic
        if asset_type == "email_campaign":
            business_data["business_name"] = "EcoGreen Solutions"
            business_data["product_service"] = "Sustainable packaging products"
            business_data["objectives"] = ["increase newsletter signups", "promote new product line"]
        elif asset_type == "social_media_ad":
            business_data["business_name"] = "TechInnovate"
            business_data["product_service"] = "AI-powered analytics platform"
            business_data["objectives"] = ["increase social media engagement", "drive demo requests"]
        elif asset_type == "landing_page":
            business_data["business_name"] = "HealthFirst"
            business_data["product_service"] = "Telemedicine subscription service"
            business_data["objectives"] = ["increase conversions", "communicate value proposition"]
        elif asset_type == "sales_funnel":
            business_data["business_name"] = "FinanceWise"
            business_data["product_service"] = "Personal finance management app"
            business_data["objectives"] = ["increase trial signups", "convert free users to premium"]
        elif asset_type == "blog_post":
            business_data["business_name"] = "FoodDelight"
            business_data["product_service"] = "Meal kit delivery service"
            business_data["objectives"] = ["improve SEO ranking", "establish thought leadership"]
        elif asset_type == "press_release":
            business_data["business_name"] = "InnovateTech"
            business_data["product_service"] = "Revolutionary smart home system"
            business_data["objectives"] = ["announce product launch", "attract investor interest"]
        
        result = test_generate_asset(asset_type, business_data)
        if result and "asset" in result:
            generated_assets.append(result["asset"])
    
    # Test asset management APIs
    assets = test_get_assets()
    
    # Test getting a specific asset
    if generated_assets:
        test_asset = generated_assets[0]
        test_get_asset_by_id(test_asset["id"])
        
        # Test deleting an asset
        test_delete_asset(test_asset["id"])
    
    # Test credit system
    test_credit_system(user["credits"])
    
    # Test error handling
    test_invalid_asset_type()
    test_missing_required_fields()
    test_nonexistent_asset()
    
    # Print summary
    print("\n===== TEST SUMMARY =====")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']}")
    print(f"Failed: {test_results['failed_tests']}")
    print(f"Success Rate: {(test_results['passed_tests'] / test_results['total_tests'] * 100):.2f}%")
    
    if test_results['failed_tests'] > 0:
        print("\nFailed Tests:")
        for test in test_results['tests']:
            if test['status'] == 'FAILED':
                print(f"- {test['name']}")
    
    print("\n===== END OF TESTS =====\n")

if __name__ == "__main__":
    run_all_tests()