#!/usr/bin/env python3
"""
Simple test script to verify LLM configuration
"""

import os
import sys

# Set API key first
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Test imports
try:
    from src.llm import chat
    print("✅ LLM module imported successfully")
except Exception as e:
    print(f"❌ LLM import failed: {e}")
    sys.exit(1)

# Test API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ API key found: {api_key[:20]}...")
else:
    print("❌ No API key found")
    sys.exit(1)

# Test chat function
try:
    print("🧪 Testing chat function...")
    response = chat([{"role": "user", "content": "Say hello in one sentence"}])
    if response and "error" not in response.lower():
        print(f"✅ Chat working: {response}")
    else:
        print(f"❌ Chat failed: {response}")
except Exception as e:
    print(f"❌ Chat error: {e}")

print("�� Test completed!")
