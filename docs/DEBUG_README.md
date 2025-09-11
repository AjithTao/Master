# Debug Tools for Backend Jira Integration

This directory contains debug tools to test and verify the backend server connection with Jira API token and other configuration details.

## Files Created

### 1. `debug_backend_jira.py` - Comprehensive Debug Tool
A full-featured debug script that performs comprehensive testing of:
- Backend server health
- Jira API token authentication
- Direct Jira connection testing
- Backend API endpoint testing
- Chat functionality testing
- Analytics endpoint testing

**Usage:**
```bash
python debug_backend_jira.py
```

### 2. `debug_simple.py` - Quick Debug Tool
A lightweight debug script for quick testing:
- Server health check
- Basic Jira connection test
- Simple chat functionality test

**Usage:**
```bash
# Quick test
python debug_simple.py

# Test specific question
python debug_simple.py "What's our current sprint status?"
```

### 3. `debug.bat` - Windows Batch File
Easy-to-use Windows batch file with menu options:
- Quick test
- Comprehensive test
- Test specific question
- Exit

**Usage:**
```cmd
debug.bat
```

## Prerequisites

1. **Backend Server Running**: Make sure your backend server is running on `http://localhost:8000`
   ```bash
   cd backend
   python main.py
   ```

2. **Jira Configuration**: Set up your Jira credentials either:
   - As environment variables:
     ```bash
     set JIRA_BASE_URL=https://your-domain.atlassian.net
     set JIRA_EMAIL=your-email@company.com
     set JIRA_API_TOKEN=your-api-token
     set JIRA_BOARD_ID=your-board-id
     ```
   - Or provide them interactively when prompted

3. **Python Dependencies**: Make sure all required packages are installed:
   ```bash
   pip install httpx asyncio
   ```

## What the Debug Tools Test

### Server Health
- ✅ Backend server is running
- ✅ Health endpoint responds correctly
- ✅ Root endpoint is accessible

### Jira Connection
- ✅ Direct Jira API connection using your credentials
- ✅ Backend API Jira connection test
- ✅ Jira configuration via backend API
- ✅ Jira status verification

### API Endpoints
- ✅ Jira search functionality
- ✅ Analytics generation
- ✅ Chat functionality with sample questions
- ✅ Error handling and response validation

### Sample Questions Tested
- "Hello, can you help me?"
- "What's our current sprint status?"
- "How many projects do we have?"
- "Who's working on what?"
- "Show me some analytics"

## Expected Output

### Successful Connection
```
✅ Server is running
✅ Connected successfully! Found X projects
✅ API connection successful: Jira connection successful! Current sprint: Sprint Name. Found X total issues.
✅ Jira configured successfully via API
✅ Chat test successful!
```

### Common Issues and Solutions

1. **"Cannot connect to backend server"**
   - Make sure backend server is running: `cd backend && python main.py`
   - Check if port 8000 is available

2. **"Jira connection failed"**
   - Verify your Jira credentials are correct
   - Check if your API token has proper permissions
   - Ensure your Jira URL is correct (include https://)

3. **"Missing Jira configuration"**
   - Set environment variables or provide them interactively
   - Make sure all required fields are provided

4. **"Chat test failed"**
   - Ensure Jira is properly configured first
   - Check backend server logs for detailed error messages

## Environment Variables

Set these environment variables for automatic configuration:

```bash
# Required
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token

# Optional
JIRA_BOARD_ID=your-board-id
```

## Troubleshooting

1. **Check Backend Logs**: Look at the backend server console for detailed error messages
2. **Verify Network**: Ensure you can access your Jira instance from your machine
3. **API Token Permissions**: Make sure your API token has read access to projects and issues
4. **Board ID**: Verify the board ID exists and is accessible with your credentials

## Next Steps

After successful debugging:
1. Your backend server is properly connected to Jira
2. You can use the chat interface to ask questions about your Jira data
3. Analytics and insights should be working correctly
4. You can clean up the debug files when no longer needed

## Cleanup

When you're done debugging, you can remove these files:
```bash
rm debug_backend_jira.py
rm debug_simple.py
rm debug.bat
```
