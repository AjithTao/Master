#!/usr/bin/env python3
"""
Test script to verify the frontend-backend-Jira integration
"""

import requests
import json
import time

# Test configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not accessible: {e}")
        return False

def test_jira_configuration():
    """Test Jira configuration endpoint"""
    try:
        # Test with dummy data
        config = {
            "url": "https://test.atlassian.net",
            "email": "test@example.com",
            "api_token": "test_token",
            "board_id": "123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/jira/configure",
            json=config,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Jira configuration endpoint is working")
            return True
        else:
            print(f"❌ Jira configuration failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Jira configuration test failed: {e}")
        return False

def test_jira_status():
    """Test Jira status endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/jira/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Jira status endpoint working - Configured: {data.get('configured', False)}")
            return True
        else:
            print(f"❌ Jira status check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Jira status test failed: {e}")
        return False

def test_chat_endpoint():
    """Test chat endpoint"""
    try:
        chat_data = {
            "message": "Hello, test message"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=chat_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Chat endpoint is working")
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat endpoint test failed: {e}")
        return False

def test_cors_headers():
    """Test CORS headers"""
    try:
        response = requests.options(
            f"{BACKEND_URL}/api/jira/status",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET"
            },
            timeout=5
        )
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        if cors_headers["Access-Control-Allow-Origin"]:
            print("✅ CORS headers are properly configured")
            return True
        else:
            print("❌ CORS headers are missing")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Frontend-Backend-Jira Integration")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Jira Configuration", test_jira_configuration),
        ("Jira Status", test_jira_status),
        ("Chat Endpoint", test_chat_endpoint),
        ("CORS Headers", test_cors_headers),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend server and configuration.")

if __name__ == "__main__":
    main()
