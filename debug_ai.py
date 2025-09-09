#!/usr/bin/env python3
"""
Debug script to test AI components and Jira integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from jira_client import JiraClient
from auth import JiraConfig
from ai_engine import AdvancedAIEngine
from query_processor import AdvancedQueryProcessor
import json

def test_entity_extraction():
    """Test entity extraction"""
    print("🔍 Testing Entity Extraction...")
    
    from query_processor import EntityExtractor
    extractor = EntityExtractor()
    
    test_queries = [
        "Give me details on story CCM-283",
        "What is CCM-283?",
        "Show me ticket CCM-283",
        "CCM-283 details"
    ]
    
    for query in test_queries:
        entities = extractor.extract_entities(query)
        print(f"Query: '{query}'")
        print(f"Entities: {entities}")
        print("---")

def test_jira_client():
    """Test Jira client connection"""
    print("\n🔍 Testing Jira Client...")
    
    try:
        # Load config
        config = JiraConfig()
        print(f"Jira URL: {config.base_url}")
        print(f"Email: {config.email}")
        print(f"API Token configured: {bool(config.api_token)}")
        
        # Test client
        client = JiraClient(config)
        print(f"Jira client created: {client is not None}")
        
        # Test search
        try:
            result = client.search("key = CCM-283", max_results=1)
            print(f"Search result: {json.dumps(result, indent=2)[:500]}...")
        except Exception as e:
            print(f"Search error: {e}")
            
    except Exception as e:
        print(f"Jira client error: {e}")

def test_ai_engine():
    """Test AI engine with Jira client"""
    print("\n🔍 Testing AI Engine...")
    
    try:
        # Load config and create client
        config = JiraConfig()
        client = JiraClient(config)
        
        # Create AI engine
        ai_engine = AdvancedAIEngine(client)
        print(f"AI Engine created: {ai_engine is not None}")
        print(f"AI Engine Jira client: {ai_engine.jira_client is not None}")
        
        # Test query processor
        query_processor = AdvancedQueryProcessor(ai_engine, client)
        print(f"Query Processor created: {query_processor is not None}")
        print(f"Query Processor Jira client: {query_processor.jira_client is not None}")
        
    except Exception as e:
        print(f"AI Engine error: {e}")

if __name__ == "__main__":
    print("🚀 Starting AI Debug Tests...\n")
    
    test_entity_extraction()
    test_jira_client()
    test_ai_engine()
    
    print("\n✅ Debug tests completed!")
