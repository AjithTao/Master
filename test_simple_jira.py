#!/usr/bin/env python3
"""
Simple test for Jira API access
"""

import asyncio
import httpx
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth import JiraConfig

async def test_simple_jira_access():
    """Test basic Jira API access"""
    print("🔍 Testing Basic Jira API Access")
    print("=" * 50)

    config = JiraConfig(
        base_url="https://taodigital.atlassian.net",
        email="ajith.ramesh@taodigitalsolutions.com",
        api_token="your_jira_api_token_here"
    )

    async with httpx.AsyncClient(auth=(config.email, config.api_token), timeout=30.0) as client:
        try:
            print("1. Testing server info...")
            url = f"{config.base_url}/rest/api/3/serverInfo"
            response = await client.get(url)
            print(f"Server info status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Server: {data.get('serverTitle', 'Unknown')}")
                print(f"Version: {data.get('version', 'Unknown')}")

            print("\n2. Testing myself endpoint...")
            url = f"{config.base_url}/rest/api/3/myself"
            response = await client.get(url)
            print(f"Myself status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"User: {data.get('displayName', 'Unknown')}")

            print("\n3. Testing projects endpoint...")
            url = f"{config.base_url}/rest/api/3/project"
            response = await client.get(url)
            print(f"Projects status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data)} projects")
                for project in data[:3]:
                    print(f"  - {project.get('key')}: {project.get('name')}")

            print("\n4. Testing simple issue search...")
            # Try a very simple search
            jql = "ORDER BY created DESC"
            url = f"{config.base_url}/rest/api/3/search?jql={jql}&maxResults=1"
            response = await client.get(url)
            print(f"Simple search status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Total issues: {data.get('total', 0)}")
                issues = data.get('issues', [])
                print(f"Issues returned: {len(issues)}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_jira_access())
