#!/usr/bin/env python3
"""
Leadership Quality Tool - Demo Script
This script helps you run a successful demo on September 19th.
"""

import os
import sys
import time
from pathlib import Path

def print_header():
    """Print demo header"""
    print("🎯 Leadership Quality Tool - Demo Script")
    print("=" * 60)
    print("Demo Date: September 19th, 2024")
    print("=" * 60)

def check_prerequisites():
    """Check if everything is ready for demo"""
    print("\n🔍 Checking demo prerequisites...")
    
    # Check if .env exists and has content
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Run: python setup.py")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check Jira configuration
    jira_url = os.getenv("JIRA_BASE_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    jira_board = os.getenv("JIRA_BOARD_ID")
    
    if not all([jira_url, jira_email, jira_token]):
        print("❌ Jira configuration incomplete")
        return False
    
    if not jira_board:
        print("⚠️  Jira board ID not set (sprint queries won't work)")
    
    # Check Confluence configuration
    conf_url = os.getenv("CONFLUENCE_BASE_URL")
    conf_email = os.getenv("CONFLUENCE_EMAIL")
    conf_token = os.getenv("CONFLUENCE_API_TOKEN")
    
    if not all([conf_url, conf_email, conf_token]):
        print("❌ Confluence configuration incomplete")
        return False
    
    # Check LLM configuration
    openai_key = os.getenv("OPENAI_API_KEY")
    aws_region = os.getenv("AWS_REGION")
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    
    if not any([openai_key, aws_region, ollama_url]):
        print("❌ No LLM provider configured")
        return False
    
    print("✅ All prerequisites met!")
    return True

def test_connections():
    """Test API connections"""
    print("\n🔗 Testing API connections...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test Jira connection
    try:
        from src.auth import JiraConfig
        from src.jira_client import JiraClient
        
        jira_cfg = JiraConfig()
        jira_client = JiraClient(jira_cfg)
        
        # Test basic search
        result = jira_client.search("project = TEST LIMIT 1", max_results=1)
        print("✅ Jira connection successful")
    except Exception as e:
        print(f"❌ Jira connection failed: {e}")
        return False
    
    # Test Confluence connection
    try:
        from src.auth import ConfluenceConfig
        from src.confluence_client import ConfluenceClient
        
        conf_cfg = ConfluenceConfig()
        conf_client = ConfluenceClient(conf_cfg)
        
        # Test basic search
        result = conf_client.search("type=page LIMIT 1", limit=1)
        print("✅ Confluence connection successful")
    except Exception as e:
        print(f"❌ Confluence connection failed: {e}")
        return False
    
    # Test LLM connection
    try:
        from src.llm import chat
        
        response = chat([{"role": "user", "content": "Hello"}])
        if response:
            print("✅ LLM connection successful")
        else:
            print("❌ LLM returned empty response")
            return False
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        return False
    
    return True

def demo_scenarios():
    """List demo scenarios"""
    print("\n🎬 Demo Scenarios")
    print("-" * 40)
    
    scenarios = [
        {
            "category": "Jira Queries",
            "queries": [
                "Give me stories worked by Ajith in current sprint",
                "List bugs closed this week by Priya",
                "Show me tickets in progress for Chart Builder team",
                "What's the velocity for last 3 sprints?"
            ]
        },
        {
            "category": "Confluence Queries",
            "queries": [
                "Find KT recording for Dataset Upload History",
                "Show me design decisions for Service Advisory Performance",
                "Summarize risks from recent retrospectives",
                "Get documentation for API changes"
            ]
        },
        {
            "category": "Cross-Tool Queries",
            "queries": [
                "Show me Chart Builder progress and attach the KT doc",
                "What's the status of Dataset Upload and find related documentation?"
            ]
        },
        {
            "category": "Error Handling",
            "queries": [
                "Show me stories by nonexistent person",
                "Find documentation that doesn't exist"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['category']}:")
        for i, query in enumerate(scenario['queries'], 1):
            print(f"   {i}. \"{query}\"")
    
    return scenarios

def run_demo():
    """Start the demo application"""
    print("\n🚀 Starting Leadership Quality Tool...")
    print("Opening Streamlit application...")
    print("URL: http://localhost:8501")
    print("\nPress Ctrl+C to stop the demo")
    
    try:
        import subprocess
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped. Thanks for using Leadership Quality!")
    except Exception as e:
        print(f"\n❌ Error starting demo: {e}")

def main():
    """Main demo function"""
    print_header()
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Demo cannot proceed. Please fix the issues above.")
        sys.exit(1)
    
    # Step 2: Test connections
    if not test_connections():
        print("\n❌ Demo cannot proceed. Please fix the connection issues.")
        sys.exit(1)
    
    # Step 3: Show demo scenarios
    scenarios = demo_scenarios()
    
    # Step 4: Start demo
    print("\n" + "=" * 60)
    print("🎯 Ready for demo!")
    print("=" * 60)
    
    choice = input("\nWould you like to start the demo now? (y/N): ").lower().strip()
    if choice == 'y':
        run_demo()
    else:
        print("\nTo start the demo manually:")
        print("1. Run: streamlit run app.py")
        print("2. Open: http://localhost:8501")
        print("3. Use the scenarios above for testing")

if __name__ == "__main__":
    main()
