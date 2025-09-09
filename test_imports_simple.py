import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("Testing imports one by one...")

print("1. Testing basic imports...")
try:
    import json
    import re
    from typing import Dict, List, Any, Optional, Tuple
    from datetime import datetime, timedelta
    from dataclasses import dataclass
    print("✅ Basic imports successful")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")

print("2. Testing numpy...")
try:
    import numpy as np
    print("✅ Numpy import successful")
except Exception as e:
    print(f"❌ Numpy import failed: {e}")

print("3. Testing auth...")
try:
    from auth import JiraConfig, LLMConfig
    print("✅ Auth import successful")
except Exception as e:
    print(f"❌ Auth import failed: {e}")

print("4. Testing llm...")
try:
    from llm import chat
    print("✅ LLM import successful")
except Exception as e:
    print(f"❌ LLM import failed: {e}")

print("5. Testing jira_client...")
try:
    from jira_client import JiraClient
    print("✅ JiraClient import successful")
except Exception as e:
    print(f"❌ JiraClient import failed: {e}")

print("6. Testing ai_engine...")
try:
    from ai_engine import AdvancedAIEngine, AIInsight
    print("✅ AI Engine import successful")
except Exception as e:
    print(f"❌ AI Engine import failed: {e}")

print("7. Testing query_processor...")
try:
    from query_processor import AdvancedQueryProcessor
    print("✅ Query Processor import successful")
except Exception as e:
    print(f"❌ Query Processor import failed: {e}")

print("8. Testing analytics_engine...")
try:
    from analytics_engine import AdvancedAnalyticsEngine
    print("✅ Analytics Engine import successful")
except Exception as e:
    print(f"❌ Analytics Engine import failed: {e}")

print("All imports completed!")

