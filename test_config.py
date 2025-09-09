import sys
import os
sys.path.append('..')

from src.auth import LLMConfig

cfg = LLMConfig()
print(f"OpenAI API Key loaded: {bool(cfg.openai_api_key)}")
print(f"Key starts with: {cfg.openai_api_key[:20] if cfg.openai_api_key else 'None'}")

# Test LLM
from src.llm import chat
try:
    response = chat([{"role": "user", "content": "Hello"}])
    print(f"LLM test successful: {response[:50]}...")
except Exception as e:
    print(f"LLM test failed: {e}")
