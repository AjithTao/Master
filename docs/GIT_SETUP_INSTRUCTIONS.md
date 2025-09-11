# Leadership Quality Tool - Git Configuration

## Manual Git Setup Instructions

Since Git is not available in the current environment, please follow these steps to push your code to GitHub:

### Step 1: Install Git (if not already installed)
1. Download Git from: https://git-scm.com/download/win
2. Install with default settings
3. Restart your terminal/command prompt

### Step 2: Initialize Git Repository
Open Command Prompt or PowerShell in your project directory and run:

```bash
# Navigate to your project directory
cd "C:\Users\Ajith\Documents\Leadership Quality Tool"

# Initialize Git repository
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: Leadership Quality Tool with AI-powered Jira integration"
```

### Step 3: Connect to GitHub Repository
```bash
# Add your GitHub repository as remote origin
git remote add origin https://github.com/AjithTao/Master.git

# Verify remote connection
git remote -v
```

### Step 4: Push to GitHub
```bash
# Push to main branch (GitHub's default)
git branch -M main
git push -u origin main
```

### Alternative: Using GitHub Desktop
1. Download GitHub Desktop from: https://desktop.github.com/
2. Install and sign in with your GitHub account
3. Click "Add an Existing Repository from your Hard Drive"
4. Select your project folder: `C:\Users\Ajith\Documents\Leadership Quality Tool`
5. Click "Publish repository" to push to GitHub

### Alternative: Using VS Code
1. Open VS Code in your project directory
2. Install the Git extension if not already installed
3. Use the Source Control panel (Ctrl+Shift+G)
4. Initialize repository and push to GitHub

## Project Files Included

The following files will be pushed to your repository:

### Backend Files
- `backend/app.py` - Main FastAPI application
- `backend/jira_client.py` - Jira API client with comprehensive fallbacks
- `backend/confluence_client.py` - Confluence API client
- `backend/auth.py` - Authentication and configuration management
- `backend/entity_extractor.py` - NLP entity extraction
- `backend/ai_summarizer.py` - OpenAI-powered summarization
- `backend/intent_router.py` - AI intent matching and routing
- `backend/data/jira_intents.json` - Intent definitions and JQL templates
- `backend/data/custom_jira_intents.json` - Custom user intents
- `backend/test_endpoints.py` - Comprehensive endpoint testing script

### Frontend Files
- `frontend/app/page.tsx` - Main application layout
- `frontend/app/components/ChatInterface.tsx` - AI chat interface
- `frontend/app/components/LeadershipInsights.tsx` - Analytics dashboard
- `frontend/app/components/DashboardPage.tsx` - Metrics dashboard
- `frontend/app/components/JiraConfigCenter.tsx` - Jira configuration
- `frontend/app/components/ConfluenceConfigCenter.tsx` - Confluence configuration
- All other React components and UI elements

### Configuration Files
- `README.md` - Comprehensive project documentation
- `package.json` - Frontend dependencies
- `requirements.txt` - Backend dependencies (if exists)

## Important Notes

1. **Environment Variables**: Make sure to create a `.env` file with your API keys before running the application
2. **Dependencies**: Install all required dependencies before running
3. **API Keys**: Ensure you have valid Jira, Confluence, and OpenAI API keys
4. **Testing**: Run the endpoint testing script to verify all functionality

## Next Steps After Pushing

1. Update the repository description on GitHub
2. Add appropriate tags/labels
3. Create issues for any known bugs or feature requests
4. Set up GitHub Actions for CI/CD if needed
5. Add collaborators if working in a team

Your Leadership Quality Tool is now ready to be shared and deployed!
