#!/usr/bin/env python3
"""
Debug script for testing backend server connection with Jira API token and other details.
This script will help verify the connection and test various API endpoints.
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth import JiraConfig
from jira_client import JiraClient

class BackendDebugger:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.jira_config = None
        self.jira_client = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        if self.jira_client:
            await self.jira_client.close()

    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")

    async def test_server_health(self) -> bool:
        """Test if the backend server is running"""
        self.print_header("Testing Backend Server Health")
        
        try:
            # Test root endpoint
            response = await self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Server is running: {data.get('message', 'Unknown')}")
                
                # Test health endpoint
                health_response = await self.client.get(f"{self.base_url}/health")
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    self.print_success(f"Health check passed: {health_data.get('status', 'Unknown')}")
                    return True
                else:
                    self.print_error(f"Health check failed: {health_response.status_code}")
                    return False
            else:
                self.print_error(f"Server not responding: {response.status_code}")
                return False
                
        except httpx.ConnectError:
            self.print_error("Cannot connect to backend server. Make sure it's running on http://localhost:8000")
            return False
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            return False

    def get_jira_config_from_user(self) -> Optional[JiraConfig]:
        """Get Jira configuration from user input"""
        self.print_header("Jira Configuration Setup")
        
        print("Please provide your Jira configuration details:")
        print("(You can also set these as environment variables)")
        
        # Try to get from environment first
        base_url = os.getenv("JIRA_BASE_URL", "")
        email = os.getenv("JIRA_EMAIL", "")
        api_token = os.getenv("JIRA_API_TOKEN", "")
        board_id = os.getenv("JIRA_BOARD_ID", "")
        
        if base_url and email and api_token:
            self.print_info("Found configuration in environment variables")
            print(f"Base URL: {base_url}")
            print(f"Email: {email}")
            print(f"API Token: {'*' * len(api_token)}")
            print(f"Board ID: {board_id}")
            
            use_env = input("\nUse environment variables? (y/n): ").lower().strip()
            if use_env == 'y':
                return JiraConfig(
                    base_url=base_url,
                    email=email,
                    api_token=api_token,
                    board_id=board_id
                )
        
        # Get from user input
        base_url = input(f"Jira Base URL [{base_url}]: ").strip() or base_url
        email = input(f"Jira Email [{email}]: ").strip() or email
        api_token = input(f"Jira API Token [{api_token}]: ").strip() or api_token
        board_id = input(f"Jira Board ID [{board_id}]: ").strip() or board_id
        
        if not all([base_url, email, api_token]):
            self.print_error("Missing required Jira configuration")
            return None
            
        return JiraConfig(
            base_url=base_url,
            email=email,
            api_token=api_token,
            board_id=board_id
        )

    async def test_jira_connection_direct(self, config: JiraConfig) -> bool:
        """Test Jira connection directly using JiraClient"""
        self.print_header("Testing Direct Jira Connection")
        
        try:
            self.jira_client = JiraClient(config)
            await self.jira_client.initialize()
            
            # Test basic connection
            self.print_info("Testing basic connection...")
            
            # Try to get projects
            projects = await self.jira_client.get_projects()
            if projects:
                self.print_success(f"Connected successfully! Found {len(projects)} projects")
                
                # Show first few projects
                for i, project in enumerate(projects[:3]):
                    print(f"  - {project.get('key', 'Unknown')}: {project.get('name', 'Unknown')}")
                if len(projects) > 3:
                    print(f"  ... and {len(projects) - 3} more projects")
                
                return True
            else:
                self.print_error("Connected but no projects found")
                return False
                
        except Exception as e:
            self.print_error(f"Direct connection failed: {e}")
            return False

    async def test_jira_connection_via_api(self, config: JiraConfig) -> bool:
        """Test Jira connection via backend API"""
        self.print_header("Testing Jira Connection via Backend API")
        
        try:
            # Test connection endpoint
            test_data = {
                "url": config.base_url,
                "email": config.email,
                "api_token": config.api_token,
                "board_id": config.board_id
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/jira/test",
                json=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.print_success(f"API connection successful: {data.get('message', '')}")
                    
                    # Show connection details
                    details = data.get("details", {})
                    if details.get("current_sprint"):
                        sprint = details["current_sprint"]
                        print(f"  Current Sprint: {sprint.get('name', 'Unknown')}")
                        print(f"  Sprint State: {sprint.get('state', 'Unknown')}")
                    
                    print(f"  Total Issues: {details.get('total_issues', 0)}")
                    return True
                else:
                    self.print_error(f"API connection failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.print_error(f"API request failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"  Error details: {error_data}")
                except:
                    print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"API connection test failed: {e}")
            return False

    async def configure_jira_via_api(self, config: JiraConfig) -> bool:
        """Configure Jira via backend API"""
        self.print_header("Configuring Jira via Backend API")
        
        try:
            config_data = {
                "url": config.base_url,
                "email": config.email,
                "api_token": config.api_token,
                "board_id": config.board_id
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/jira/configure",
                json=config_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.print_success("Jira configured successfully via API")
                    return True
                else:
                    self.print_error(f"Configuration failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.print_error(f"Configuration request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Configuration failed: {e}")
            return False

    async def test_jira_status(self) -> bool:
        """Test Jira status endpoint"""
        self.print_header("Testing Jira Status")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/jira/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("configured"):
                    self.print_success("Jira is configured and ready")
                    print(f"  Board ID: {data.get('board_id', 'Not set')}")
                    config = data.get("config", {})
                    if config:
                        print(f"  URL: {config.get('url', 'Not set')}")
                        print(f"  Email: {config.get('email', 'Not set')}")
                    return True
                else:
                    self.print_info("Jira is not configured")
                    return False
            else:
                self.print_error(f"Status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Status check failed: {e}")
            return False

    async def test_jira_search(self) -> bool:
        """Test Jira search functionality"""
        self.print_header("Testing Jira Search")
        
        try:
            # Test basic search
            search_data = {
                "jql": "project is not EMPTY",
                "max_results": 5
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/jira/search",
                json=search_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result = data.get("result", {})
                    issues = result.get("issues", [])
                    total = result.get("total", 0)
                    
                    self.print_success(f"Search successful! Found {total} total issues")
                    
                    # Show first few issues
                    for i, issue in enumerate(issues[:3]):
                        key = issue.get("key", "Unknown")
                        fields = issue.get("fields", {})
                        summary = fields.get("summary", "No summary")
                        status = fields.get("status", {}).get("name", "Unknown")
                        print(f"  {i+1}. {key}: {summary} [{status}]")
                    
                    if len(issues) > 3:
                        print(f"  ... and {len(issues) - 3} more issues")
                    
                    return True
                else:
                    self.print_error("Search failed")
                    return False
            else:
                self.print_error(f"Search request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Search test failed: {e}")
            return False

    async def test_chat_functionality(self) -> bool:
        """Test chat functionality with sample questions"""
        self.print_header("Testing Chat Functionality")
        
        test_questions = [
            "Hello, can you help me?",
            "What's our current sprint status?",
            "How many projects do we have?",
            "Who's working on what?",
            "Show me some analytics"
        ]
        
        success_count = 0
        
        for i, question in enumerate(test_questions, 1):
            print(f"\nTest {i}: {question}")
            
            try:
                chat_data = {
                    "message": question,
                    "messages": []
                }
                
                response = await self.client.post(
                    f"{self.base_url}/api/chat",
                    json=chat_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        response_text = data.get("response", "")
                        metadata = data.get("metadata", {})
                        
                        print(f"✅ Response: {response_text[:100]}{'...' if len(response_text) > 100 else ''}")
                        print(f"   Query Type: {metadata.get('query_type', 'Unknown')}")
                        print(f"   Confidence: {metadata.get('confidence', 0):.2f}")
                        
                        success_count += 1
                    else:
                        print(f"❌ Chat failed: {data.get('response', 'Unknown error')}")
                else:
                    print(f"❌ Chat request failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Chat test failed: {e}")
        
        self.print_info(f"Chat tests completed: {success_count}/{len(test_questions)} successful")
        return success_count > 0

    async def test_analytics_endpoint(self) -> bool:
        """Test analytics endpoint"""
        self.print_header("Testing Analytics Endpoint")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/jira/analytics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    analytics = data.get("analytics", {})
                    summary = analytics.get("summary", {})
                    
                    self.print_success("Analytics generated successfully")
                    print(f"  Total Issues: {summary.get('total_issues', 0)}")
                    print(f"  Total Projects: {summary.get('total_projects', 0)}")
                    print(f"  Total Stories: {summary.get('total_stories', 0)}")
                    print(f"  Total Defects: {summary.get('total_defects', 0)}")
                    print(f"  Total Tasks: {summary.get('total_tasks', 0)}")
                    print(f"  Team Members: {summary.get('total_assignees', 0)}")
                    
                    return True
                else:
                    self.print_error("Analytics generation failed")
                    return False
            else:
                self.print_error(f"Analytics request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Analytics test failed: {e}")
            return False

    async def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        self.print_header("Starting Comprehensive Backend Debug Test")
        print(f"Testing backend at: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Test 1: Server Health
        if not await self.test_server_health():
            self.print_error("Server health check failed. Exiting.")
            return False
        
        # Test 2: Get Jira Configuration
        self.jira_config = self.get_jira_config_from_user()
        if not self.jira_config:
            self.print_error("Jira configuration failed. Exiting.")
            return False
        
        # Test 3: Direct Jira Connection
        direct_success = await self.test_jira_connection_direct(self.jira_config)
        
        # Test 4: API Jira Connection Test
        api_test_success = await self.test_jira_connection_via_api(self.jira_config)
        
        # Test 5: Configure Jira via API
        if api_test_success:
            config_success = await self.configure_jira_via_api(self.jira_config)
            
            if config_success:
                # Test 6: Check Jira Status
                await self.test_jira_status()
                
                # Test 7: Test Jira Search
                await self.test_jira_search()
                
                # Test 8: Test Chat Functionality
                await self.test_chat_functionality()
                
                # Test 9: Test Analytics
                await self.test_analytics_endpoint()
        
        # Summary
        self.print_header("Test Summary")
        if direct_success:
            self.print_success("Direct Jira connection: PASSED")
        else:
            self.print_error("Direct Jira connection: FAILED")
            
        if api_test_success:
            self.print_success("API Jira connection: PASSED")
        else:
            self.print_error("API Jira connection: FAILED")
        
        self.print_info("Debug test completed!")
        return True

async def main():
    """Main function"""
    print("🔍 Backend Jira Debug Tool")
    print("This tool will test your backend server connection with Jira API")
    print("Make sure your backend server is running on http://localhost:8000")
    
    async with BackendDebugger() as debugger:
        await debugger.run_comprehensive_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Debug test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Debug test failed with error: {e}")
        import traceback
        traceback.print_exc()
