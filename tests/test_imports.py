from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime
import logging
import sys
import asyncio
from contextlib import asynccontextmanager

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test imports one by one
try:
    from jira_client import JiraClient
    print("✅ JiraClient import successful")
except Exception as e:
    print(f"❌ JiraClient import failed: {e}")

try:
    from auth import JiraConfig
    print("✅ JiraConfig import successful")
except Exception as e:
    print(f"❌ JiraConfig import failed: {e}")

try:
    from ai_engine import AdvancedAIEngine, AIInsight
    print("✅ AI Engine import successful")
except Exception as e:
    print(f"❌ AI Engine import failed: {e}")

try:
    from query_processor import AdvancedQueryProcessor
    print("✅ Query Processor import successful")
except Exception as e:
    print(f"❌ Query Processor import failed: {e}")

try:
    from analytics_engine import AdvancedAnalyticsEngine
    print("✅ Analytics Engine import successful")
except Exception as e:
    print(f"❌ Analytics Engine import failed: {e}")

# Simple FastAPI app
app = FastAPI(title="Test Integration Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Integration Hub API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

