#!/usr/bin/env python3
"""
Test script for comparative queries enhancement
"""

import asyncio
import json
from intelligent_ai_engine import IntelligentAIEngine
from jira_client import JiraClient
from auth import JiraConfig

async def test_comparative_queries():
    """Test comparative query handling"""
    
    print("🔍 Testing Comparative Query Enhancement")
    print("=" * 50)
    
    # Mock Jira client for testing
    class MockJiraClient:
        def get_all_projects(self):
            return [
                {'key': 'CCM', 'name': 'Call Classification Modernization'},
                {'key': 'TI', 'name': 'TAO Intranet'},
                {'key': 'CES', 'name': 'Candidate Evaluation System'}
            ]
        
        def get_known_project_keys(self):
            return ['CCM', 'TI', 'CES']
        
        def get_known_assignee_names(self):
            return ['Ashwin Thyagarajan', 'SARAVANAN NP', 'Karthikeya', 'Ashwini Kumar']
        
        async def search(self, jql, **kwargs):
            # Mock search results based on JQL
            print(f"  🔍 Executing JQL: {jql}")
            
            # Simulate different results for different queries
            if 'Ashwin Thyagarajan' in jql:
                return {
                    'issues': [
                        {
                            'key': 'CCM-283',
                            'fields': {
                                'summary': 'HCAT_72 Model Optimization',
                                'status': {'name': 'To Do'},
                                'issuetype': {'name': 'Story'},
                                'priority': {'name': 'Medium'},
                                'assignee': {'displayName': 'Ashwin Thyagarajan'}
                            }
                        },
                        {
                            'key': 'CCM-285',
                            'fields': {
                                'summary': 'Another task',
                                'status': {'name': 'In Progress'},
                                'issuetype': {'name': 'Task'},
                                'priority': {'name': 'High'},
                                'assignee': {'displayName': 'Ashwin Thyagarajan'}
                            }
                        }
                    ]
                }
            elif 'SARAVANAN NP' in jql:
                return {
                    'issues': [
                        {
                            'key': 'TI-123',
                            'fields': {
                                'summary': 'UI Enhancement',
                                'status': {'name': 'In Progress'},
                                'issuetype': {'name': 'Story'},
                                'priority': {'name': 'Medium'},
                                'assignee': {'displayName': 'SARAVANAN NP'}
                            }
                        }
                    ]
                }
            elif 'CCM' in jql and 'priority = \'High\'' in jql:
                return {
                    'issues': [
                        {
                            'key': 'CCM-290',
                            'fields': {
                                'summary': 'Critical Bug Fix',
                                'status': {'name': 'To Do'},
                                'issuetype': {'name': 'Bug'},
                                'priority': {'name': 'High'},
                                'assignee': {'displayName': 'Karthikeya'}
                            }
                        }
                    ]
                }
            elif 'CES' in jql and 'priority = \'High\'' in jql:
                return {
                    'issues': [
                        {
                            'key': 'CES-45',
                            'fields': {
                                'summary': 'Security Enhancement',
                                'status': {'name': 'Done'},
                                'issuetype': {'name': 'Story'},
                                'priority': {'name': 'High'},
                                'assignee': {'displayName': 'Ashwini Kumar'}
                            }
                        },
                        {
                            'key': 'CES-46',
                            'fields': {
                                'summary': 'Performance Fix',
                                'status': {'name': 'To Do'},
                                'issuetype': {'name': 'Task'},
                                'priority': {'name': 'High'},
                                'assignee': {'displayName': 'Ashwini Kumar'}
                            }
                        }
                    ]
                }
            else:
                return {'issues': []}
    
    # Create mock AI engine (without OpenAI for testing)
    mock_client = MockJiraClient()
    ai_engine = IntelligentAIEngine(mock_client)
    ai_engine.client = None  # Disable OpenAI for testing
    
    # Test cases
    test_queries = [
        "Who's busier: Ashwin Thyagarajan or SARAVANAN NP?",
        "Which project has more urgent work: CCM or CES?",
        "Compare Ashwin vs SARAVANAN workload",
        "CCM vs TI project comparison"
    ]
    
    for query in test_queries:
        print(f"\n🧪 Testing Query: '{query}'")
        print("-" * 30)
        
        try:
            result = await ai_engine.process_query(query)
            
            if result.get('success'):
                print(f"✅ Intent: {result.get('intent', 'Unknown')}")
                print(f"📊 JQL: {result.get('jql', 'No JQL')}")
                
                if result.get('comparison_data'):
                    print("🔍 Comparison Data:")
                    for comp_data in result['comparison_data']:
                        entity = comp_data['entity']
                        count = comp_data['count']
                        print(f"  - {entity}: {count} items")
                else:
                    print(f"📝 Data: {len(result.get('data', []))} items")
                
                print(f"💬 Response Preview: {result.get('response', '')[:100]}...")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Comparative Query Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_comparative_queries())
