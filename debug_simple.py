#!/usr/bin/env python3
"""
Simple debug script for quick testing of backend server and Jira connection.
This is a lightweight version for quick checks.
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth import JiraConfig
from jira_client import JiraClient

async def quick_test():
    """Quick test of backend server and Jira connection"""
    print("🚀 Quick Backend & Jira Debug Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Server Health
        print("\n1. Testing server health...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Server is running")
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("Make sure backend server is running on http://localhost:8000")
            return
        
        # Test 2: Get Jira config
        print("\n2. Getting Jira configuration...")
        
        # Try environment variables first
        jira_url = os.getenv("JIRA_BASE_URL", "")
        jira_email = os.getenv("JIRA_EMAIL", "")
        jira_token = os.getenv("JIRA_API_TOKEN", "")
        jira_board = os.getenv("JIRA_BOARD_ID", "")
        
        if not all([jira_url, jira_email, jira_token]):
            print("❌ Missing Jira configuration in environment variables")
            print("Please set: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
            return
        
        print(f"✅ Found Jira config: {jira_url} ({jira_email})")
        
        # Test 3: Direct Jira connection
        print("\n3. Testing direct Jira connection...")
        try:
            config = JiraConfig(
                base_url=jira_url,
                email=jira_email,
                api_token=jira_token,
                board_id=jira_board
            )
            
            jira_client = JiraClient(config)
            await jira_client.initialize()
            
            # Test with a simple search
            result = await jira_client.search("project is not EMPTY", max_results=1)
            total_issues = result.get('total', 0)
            
            print(f"✅ Direct Jira connection successful! Found {total_issues} total issues")
            
            await jira_client.close()
            
        except Exception as e:
            print(f"❌ Direct Jira connection failed: {e}")
            return
        
        # Test 4: Backend API connection test
        print("\n4. Testing backend API connection...")
        try:
            test_data = {
                "url": jira_url,
                "email": jira_email,
                "api_token": jira_token,
                "board_id": jira_board
            }
            
            response = await client.post(f"{base_url}/api/jira/test", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ Backend API connection successful: {data.get('message', '')}")
                else:
                    print(f"❌ Backend API connection failed: {data.get('message', '')}")
                    return
            else:
                print(f"❌ Backend API request failed: {response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Backend API test failed: {e}")
            return
        
        # Test 5: Configure Jira via API
        print("\n5. Configuring Jira via backend API...")
        try:
            config_data = {
                "url": jira_url,
                "email": jira_email,
                "api_token": jira_token,
                "board_id": jira_board
            }
            
            response = await client.post(f"{base_url}/api/jira/configure", json=config_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Jira configured successfully via API")
                else:
                    print(f"❌ Configuration failed: {data.get('message', '')}")
                    return
            else:
                print(f"❌ Configuration request failed: {response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Configuration failed: {e}")
            return
        
        # Test 6: Test chat functionality
        print("\n6. Testing chat functionality...")
        try:
            chat_data = {
                "message": "What's our current sprint status?",
                "messages": []
            }
            
            response = await client.post(f"{base_url}/api/chat", json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response_text = data.get("response", "")
                    print(f"✅ Chat test successful!")
                    print(f"   Response: {response_text[:100]}{'...' if len(response_text) > 100 else ''}")
                else:
                    print(f"❌ Chat test failed: {data.get('response', '')}")
            else:
                print(f"❌ Chat request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Chat test failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Quick test completed!")
        print("All basic functionality appears to be working.")

async def test_specific_question(question: str):
    """Test a specific question via the chat API"""
    print(f"\n🔍 Testing specific question: '{question}'")
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            chat_data = {
                "message": question,
                "messages": []
            }
            
            response = await client.post(f"{base_url}/api/chat", json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response_text = data.get("response", "")
                    metadata = data.get("metadata", {})
                    
                    print(f"✅ Question processed successfully!")
                    print(f"📝 Response: {response_text}")
                    print(f"🔍 Query Type: {metadata.get('query_type', 'Unknown')}")
                    print(f"📊 Confidence: {metadata.get('confidence', 0):.2f}")
                else:
                    print(f"❌ Question processing failed: {data.get('response', '')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific question
        question = " ".join(sys.argv[1:])
        asyncio.run(test_specific_question(question))
    else:
        # Run quick test
        try:
            asyncio.run(quick_test())
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
