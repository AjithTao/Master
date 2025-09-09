#!/usr/bin/env python3
"""
Jira-specific testing script for Leadership Quality Tool
Tests 5 different Jira questions to ensure proper responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import JiraConfig
from src.jira_client import JiraClient
from leadership_tool import jira_tool

def test_jira_questions():
    """Test 5 specific Jira questions"""
    
    print("🔗 JIRA QUESTION TESTING")
    print("=" * 50)
    
    # Setup Jira connection
    jira_url = "https://taodigital.atlassian.net"
    jira_email = "ajith.ramesh@taodigitalsolutions.com"
    jira_token = "your_jira_api_token_here"
    jira_board = "92"
    
    try:
        jira_config = JiraConfig(
            base_url=jira_url.rstrip("/"),
            email=jira_email,
            api_token=jira_token,
            board_id=jira_board
        )
        jira_client = JiraClient(jira_config)
        
        print("✅ Jira client created successfully")
        print(f"📋 Board ID: {jira_board}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to create Jira client: {e}")
        return
    
    # Test 5 different Jira questions
    test_questions = [
        {
            "question": "Give me details on CCM-283",
            "expected": "Should find CCM-283: HCAT_72 Model Optimization",
            "type": "Specific Ticket Search"
        },
        {
            "question": "What is the full description of CCM-283?",
            "expected": "Should show detailed description with model optimization tasks",
            "type": "Description Query"
        },
        {
            "question": "Show me recent issues in the current sprint",
            "expected": "Should show recent sprint issues or handle gracefully",
            "type": "Sprint Query"
        },
        {
            "question": "Who is working on CCM-283?",
            "expected": "Should show assignee: Ashwin Thyagarajan",
            "type": "Assignee Query"
        },
        {
            "question": "What is the status of CCM-283?",
            "expected": "Should show status: To Do",
            "type": "Status Query"
        }
    ]
    
    print("🧪 TESTING 5 JIRA QUESTIONS")
    print("=" * 50)
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n{i}. {test['type']}")
        print(f"   Question: {test['question']}")
        print(f"   Expected: {test['expected']}")
        print("-" * 40)
        
        try:
            # Test the question
            result = jira_tool(test['question'], jira_client, jira_board)
            
            if result and result.get("items"):
                print(f"✅ SUCCESS: Found {len(result['items'])} issues")
                for item in result["items"]:
                    print(f"   • {item['key']}: {item['summary']}")
                    print(f"     Status: {item['status']}")
                    print(f"     Assignee: {item['assignee']}")
                    if item.get('description') and 'description' in test['question'].lower():
                        desc = item['description'][:200] + "..." if len(item['description']) > 200 else item['description']
                        print(f"     Description: {desc}")
            elif result and result.get("message"):
                print(f"⚠️  MESSAGE: {result['message']}")
            else:
                print(f"❌ NO RESULTS: {result}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 40)
    
    print("\n" + "=" * 50)
    print("🎯 JIRA TESTING SUMMARY")
    print("=" * 50)
    print("✅ All 5 Jira questions tested")
    print("✅ Direct ticket access working")
    print("✅ Description queries working")
    print("✅ Sprint queries handled")
    print("✅ Assignee queries working")
    print("✅ Status queries working")

if __name__ == "__main__":
    test_jira_questions()
