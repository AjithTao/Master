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

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jira_client import JiraClient
from auth import JiraConfig
from ai_engine import AdvancedAIEngine, AIInsight
from query_processor import AdvancedQueryProcessor
from analytics_engine import AdvancedAnalyticsEngine

# Simple app state (no lifespan manager)
class AppState:
    def __init__(self):
        self.jira_configured = False
        self.jira_client = None
        self.jira_config = None
        self.jira_board_id = None
        self.messages = []
        self.export_files = {}
        self.ai_engine = None
        self.query_processor = None
        self.analytics_engine = None

app_state = AppState()

# FastAPI app
app = FastAPI(title="Integration Hub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    message: str

class JiraConfigRequest(BaseModel):
    url: str
    email: str
    api_token: str
    board_id: str

# Routes
@app.get("/")
async def root():
    return {"message": "Integration Hub API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/jira/configure")
async def configure_jira(config: JiraConfigRequest):
    """Configure Jira connection"""
    try:
        jira_config = JiraConfig(
            base_url=config.url,
            email=config.email,
            api_token=config.api_token,
            board_id=config.board_id
        )
        jira_client = JiraClient(jira_config)
        await jira_client.initialize()
        
        app_state.jira_configured = True
        app_state.jira_client = jira_client
        app_state.jira_config = jira_config
        app_state.jira_board_id = config.board_id
        
        return {
            "success": True,
            "message": "Jira configured successfully",
            "config": {
                "url": config.url,
                "email": config.email,
                "board_id": config.board_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Handle chat messages with advanced AI processing"""
    try:
        message = request.message.strip()
        
        # Check if Jira is configured
        if not app_state.jira_configured:
            return {
                "response": "Jira is not configured. Please configure Jira first.",
                "success": False,
                "metadata": {"ai_enhanced": False, "error": True}
            }
        
        # Initialize AI components lazily
        if not app_state.ai_engine:
            app_state.ai_engine = AdvancedAIEngine(app_state.jira_client)
        
        if not app_state.query_processor:
            app_state.query_processor = AdvancedQueryProcessor(app_state.ai_engine, app_state.jira_client)
        
        # Process query
        query_result = await app_state.query_processor.process_query(message)
        response = query_result.get('response', 'I apologize, but I encountered an issue processing your request.')
        
        return {
            "response": response,
            "success": True,
            "metadata": {
                "query_type": query_result.get('type', 'unknown'),
                "confidence": query_result.get('confidence', 0.0),
                "ai_enhanced": True
            }
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "success": False,
            "metadata": {"ai_enhanced": False, "error": True}
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

