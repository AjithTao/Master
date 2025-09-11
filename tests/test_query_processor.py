import sys
import os
sys.path.append('.')

# Test the query processor directly
from src.ai_engine import AdvancedAIEngine
from src.query_processor import AdvancedQueryProcessor
from src.jira_client import JiraClient, JiraConfig

# Create a mock Jira client
jira_config = JiraConfig(
    base_url="https://taodigital.atlassian.net",
    email="test@example.com", 
    api_token="test_token",
    board_id="123"
)

jira_client = JiraClient(jira_config)

# Create AI engine
ai_engine = AdvancedAIEngine(jira_client)

# Create query processor
query_processor = AdvancedQueryProcessor(ai_engine, jira_client)

# Test query processing
import asyncio

async def test_query():
    result = await query_processor.process_query("what stories are assigned to karthikeyan?")
    print(f"Query result: {result}")

asyncio.run(test_query())
