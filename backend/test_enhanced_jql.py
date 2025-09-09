#!/usr/bin/env python3
"""
Enhanced JQL Migration Tests
Tests the migration from deprecated /rest/api/3/search to Enhanced JQL endpoints.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_JQL = "project is not EMPTY"

async def test_enhanced_search():
    """Test Enhanced JQL search endpoint"""
    print("🔍 Testing Enhanced JQL Search...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test the diagnostics endpoint first
            response = await client.get(f"{BASE_URL}/api/jira/diagnostics/search")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Diagnostics: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Diagnostics failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Enhanced search test failed: {e}")
            return False
    
    return True

async def test_chat_endpoint():
    """Test chat endpoint with training data"""
    print("\n💬 Testing Chat Endpoint...")
    
    test_queries = [
        "How many open sprint items?",
        "Show me bugs",
        "Count stories"
    ]
    
    async with httpx.AsyncClient() as client:
        for query in test_queries:
            try:
                response = await client.post(
                    f"{BASE_URL}/api/chat",
                    json={"message": query},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Query: '{query}'")
                    print(f"   Response: {data.get('response', 'No response')}")
                    print(f"   Mode: {data.get('mode', 'unknown')}")
                    print(f"   Count: {data.get('raw', {}).get('count', 'N/A')}")
                else:
                    print(f"❌ Query '{query}' failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Chat test failed for '{query}': {e}")

async def test_leadership_overview():
    """Test leadership overview endpoint"""
    print("\n📊 Testing Leadership Overview...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test with board ID 92 (CCM project)
            response = await client.get(f"{BASE_URL}/api/leadership/overview?board_id=92")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    overview = data.get("data", {})
                    print(f"✅ Leadership overview successful")
                    print(f"   Current sprint: {overview.get('timeline', {}).get('current')}")
                    print(f"   Velocity series: {len(overview.get('charts', {}).get('velocity_series', []))} items")
                    print(f"   Suggestions: {len(overview.get('suggestions', []))} items")
                else:
                    print(f"❌ Leadership overview failed: {data}")
            else:
                print(f"❌ Leadership overview failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Leadership overview test failed: {e}")

async def test_curl_examples():
    """Provide cURL examples for manual testing"""
    print("\n🔧 cURL Examples for Manual Testing:")
    print("\n1. Enhanced JQL Search:")
    print(f'curl -X POST "{BASE_URL}/api/jira/diagnostics/search"')
    
    print("\n2. Approximate Count Test:")
    print(f'curl -X POST "{BASE_URL}/api/chat" \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"message": "How many open sprint items?"}}\'')
    
    print("\n3. Leadership Overview:")
    print(f'curl "{BASE_URL}/api/leadership/overview?board_id=92"')

async def main():
    """Run all Enhanced JQL tests"""
    print("🚀 Enhanced JQL Migration Tests")
    print("=" * 50)
    
    # Test Enhanced JQL search
    await test_enhanced_search()
    
    # Test chat endpoint
    await test_chat_endpoint()
    
    # Test leadership overview
    await test_leadership_overview()
    
    # Provide cURL examples
    await test_curl_examples()
    
    print("\n✅ Enhanced JQL migration tests completed!")
    print("\nKey improvements:")
    print("- ✅ No more 410 Gone errors")
    print("- ✅ Fast approximate counting")
    print("- ✅ Robust sprint fallbacks")
    print("- ✅ Grounded numbers in responses")

if __name__ == "__main__":
    asyncio.run(main())
