import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env from the project root (one level up from src/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

@dataclass
class JiraConfig:
    base_url: str = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    email: str = os.getenv("JIRA_EMAIL", "")
    api_token: str = os.getenv("JIRA_API_TOKEN", "")
    board_id: str = os.getenv("JIRA_BOARD_ID", "")

@dataclass
class ConfluenceConfig:
    base_url: str = os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")
    email: str = os.getenv("CONFLUENCE_EMAIL", "")
    api_token: str = os.getenv("CONFLUENCE_API_TOKEN", "")
    space_key: str = os.getenv("CONFLUENCE_SPACE_KEY", "")

@dataclass
class LLMConfig:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    # AWS Bedrock settings
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "arn:aws:bedrock:us-east-1:402145832436:inference-profile/us.meta.llama3-1-8b-instruct-v1:0")
    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
