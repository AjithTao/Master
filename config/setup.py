#!/usr/bin/env python3
"""
Leadership Quality Tool - Setup Script
This script helps you configure the environment for the Leadership Quality chatbot.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return False
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        print("Please ensure you're running this script from the project root directory.")
        return False
    
    # Copy .env.example to .env
    with open(env_example, 'r') as src:
        content = src.read()
    
    with open(env_file, 'w') as dst:
        dst.write(content)
    
    print("✅ Created .env file from template")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'streamlit', 'requests', 'pandas', 'pydantic', 
        'beautifulsoup4', 'langchain', 'faiss-cpu', 'openai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\nInstall them with:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def validate_config():
    """Validate the current configuration"""
    print("\n🔍 Validating configuration...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found. Run setup first.")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check Jira configuration
    jira_url = os.getenv("JIRA_BASE_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    
    if not all([jira_url, jira_email, jira_token]):
        print("⚠️  Jira configuration incomplete")
    else:
        print("✅ Jira configuration found")
    
    # Check Confluence configuration
    conf_url = os.getenv("CONFLUENCE_BASE_URL")
    conf_email = os.getenv("CONFLUENCE_EMAIL")
    conf_token = os.getenv("CONFLUENCE_API_TOKEN")
    
    if not all([conf_url, conf_email, conf_token]):
        print("⚠️  Confluence configuration incomplete")
    else:
        print("✅ Confluence configuration found")
    
    # Check LLM configuration
    openai_key = os.getenv("OPENAI_API_KEY")
    aws_region = os.getenv("AWS_REGION")
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    
    if not any([openai_key, aws_region, ollama_url]):
        print("⚠️  No LLM provider configured")
    else:
        if openai_key:
            print("✅ OpenAI configuration found")
        if aws_region:
            print("✅ AWS Bedrock configuration found")
        if ollama_url:
            print("✅ Ollama configuration found")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Leadership Quality Tool - Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Step 1: Check dependencies
    print("\n1️⃣ Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Create .env file
    print("\n2️⃣ Setting up environment file...")
    if not create_env_file():
        sys.exit(1)
    
    # Step 3: Validate configuration
    print("\n3️⃣ Validating configuration...")
    validate_config()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your actual credentials")
    print("2. Run: streamlit run app.py")
    print("3. Open http://localhost:8501 in your browser")
    print("\nFor help, see README.md")

if __name__ == "__main__":
    main()
