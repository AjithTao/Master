#!/usr/bin/env python3
"""
Detailed debug test
"""

import os
import sys

# Set API key first
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

print("🔍 Debugging LLM configuration...")

# Check environment variable
api_key = os.getenv("OPENAI_API_KEY")
print(f"Environment API key: {api_key[:20] if api_key else 'None'}...")

# Test OpenAI import
try:
    from openai import OpenAI
    print("✅ OpenAI module imported")
    
    # Test direct client creation
    if api_key:
        client = OpenAI(api_key=api_key)
        print("✅ Direct client creation successful")
        
        # Test API call
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say hello"}],
                temperature=0.2
            )
            print(f"✅ Direct API call successful: {resp.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Direct API call failed: {e}")
    else:
        print("❌ No API key for direct test")
        
except Exception as e:
    print(f"❌ OpenAI import failed: {e}")

# Test our LLM module
try:
    from src.llm import chat, _openai_client
    print("✅ LLM module imported")
    
    # Test _openai_client function
    client = _openai_client()
    if client:
        print("✅ _openai_client() returned client")
    else:
        print("❌ _openai_client() returned None")
    
    # Test chat function
    response = chat([{"role": "user", "content": "Say hello"}])
    print(f"Chat response: {response}")
    
except Exception as e:
    print(f"❌ LLM module test failed: {e}")

print("🎉 Debug completed!")
