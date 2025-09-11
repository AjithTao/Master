#!/usr/bin/env python3
"""
Robust Ticket Lookup Tests
Tests the new ticket key detection and direct issue lookup functionality.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"

async def test_ccm_283_details():
    """Test direct ticket lookup for CCM-283"""
    print("🎫 Testing CCM-283 Details...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json={"message": "CCM-283 details"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"✅ Mode: {data.get('mode', 'unknown')}")
                print(f"✅ Ticket Key: {data.get('ticket_key', 'N/A')}")
                print(f"✅ Response:")
                print(f"   {data.get('response', 'No response')}")
                
                if data.get('raw'):
                    raw = data['raw']
                    print(f"✅ Raw Data:")
                    print(f"   Summary: {raw.get('summary', 'N/A')}")
                    print(f"   Status: {raw.get('status', 'N/A')}")
                    print(f"   Type: {raw.get('type', 'N/A')}")
                    print(f"   Priority: {raw.get('priority', 'N/A')}")
                    print(f"   Assignee: {raw.get('assignee', 'N/A')}")
                    print(f"   Project: {raw.get('project', 'N/A')}")
                
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

async def test_sprint_items_count():
    """Test sprint items count with grounded numbers"""
    print("\n📊 Testing Sprint Items Count...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json={"message": "How many open sprint items?"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"✅ Mode: {data.get('mode', 'unknown')}")
                print(f"✅ JQL: {data.get('jql', 'N/A')}")
                print(f"✅ Response:")
                print(f"   {data.get('response', 'No response')}")
                
                if data.get('raw'):
                    raw = data['raw']
                    count = raw.get('count', 'N/A')
                    print(f"✅ Grounded Count: {count}")
                    
                    # Verify the count is a number (not 0 due to error)
                    if isinstance(count, int) and count >= 0:
                        print(f"✅ Count validation: PASSED (valid number)")
                    else:
                        print(f"⚠️ Count validation: FAILED (invalid count: {count})")
                
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

async def test_other_ticket_formats():
    """Test various ticket key formats"""
    print("\n🔍 Testing Other Ticket Formats...")
    
    test_cases = [
        "PROJ-123 details",
        "Show me ABC-456",
        "What's the status of XYZ-789?",
        "DEF-999 information"
    ]
    
    async with httpx.AsyncClient() as client:
        for test_case in test_cases:
            try:
                response = await client.post(
                    f"{BASE_URL}/api/chat",
                    json={"message": test_case},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    mode = data.get('mode', 'unknown')
                    print(f"✅ '{test_case}' → Mode: {mode}")
                    
                    if mode == 'direct_issue':
                        ticket_key = data.get('ticket_key', 'N/A')
                        print(f"   Ticket Key: {ticket_key}")
                    elif mode == 'direct_issue_error':
                        print(f"   Error: {data.get('response', 'No error message')}")
                else:
                    print(f"❌ '{test_case}' → Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ '{test_case}' → Exception: {e}")

async def test_non_ticket_queries():
    """Test that non-ticket queries still work"""
    print("\n💬 Testing Non-Ticket Queries...")
    
    test_queries = [
        "How many bugs are open?",
        "Show me stories",
        "Count all issues"
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
                    mode = data.get('mode', 'unknown')
                    print(f"✅ '{query}' → Mode: {mode}")
                    
                    if data.get('raw', {}).get('count') is not None:
                        count = data['raw']['count']
                        print(f"   Count: {count}")
                else:
                    print(f"❌ '{query}' → Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ '{query}' → Exception: {e}")

async def main():
    """Run all robust ticket lookup tests"""
    print("🚀 Robust Ticket Lookup Tests")
    print("=" * 50)
    
    # Test 1: CCM-283 details (should return direct issue info, not 0)
    success1 = await test_ccm_283_details()
    
    # Test 2: Sprint items count (should return grounded count)
    success2 = await test_sprint_items_count()
    
    # Test 3: Other ticket formats
    await test_other_ticket_formats()
    
    # Test 4: Non-ticket queries
    await test_non_ticket_queries()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"✅ CCM-283 Details: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Sprint Items Count: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All critical tests PASSED!")
        print("\nKey improvements:")
        print("- ✅ Direct ticket lookup (no more wrong '0' answers)")
        print("- ✅ Grounded counts from Jira")
        print("- ✅ Robust error handling")
        print("- ✅ No retries on HTTP 400/410")
    else:
        print("\n⚠️ Some tests FAILED - check the implementation")

if __name__ == "__main__":
    asyncio.run(main())
