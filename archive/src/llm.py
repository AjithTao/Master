from typing import List, Dict, Any
from auth import LLMConfig
import requests
import os
import json

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import boto3
    from botocore.exceptions import ClientError
except Exception:
    boto3 = None

cfg = LLMConfig()

def _openai_client():
    # Use the API key from configuration
    api_key = cfg.openai_api_key
    if not api_key or OpenAI is None:
        return None
    return OpenAI(api_key=api_key)

def _bedrock_client():
    if not boto3:
        return None
    try:
        bedrock = boto3.client('bedrock-runtime', region_name=cfg.aws_region)
        return bedrock
    except Exception:
        return None

def chat(messages: List[Dict[str, str]], model: str | None = None) -> str:
    print(f"🔍 LLM: Starting chat with {len(messages)} messages")
    print(f"🔍 LLM: Model: {model or 'gpt-4o-mini'}")
    
    # Try OpenAI first
    client = _openai_client()
    if client:
        try:
            print("🔍 LLM: Using OpenAI client")
            resp = client.chat.completions.create(
                model=model or "gpt-4o-mini",
                messages=messages,
                temperature=0.2
            )
            response = resp.choices[0].message.content.strip()
            print(f"🔍 LLM: OpenAI response: {response[:100]}...")
            return response
        except Exception as e:
            print(f"❌ LLM: OpenAI error: {e}")
            return f"Error: Unable to connect to OpenAI. Please check your internet connection and try again."
    
    # If no OpenAI, return error
    print("❌ LLM: No OpenAI client available")
    return "Error: OpenAI API key not configured properly."
