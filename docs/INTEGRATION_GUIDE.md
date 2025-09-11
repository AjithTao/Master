# Leadership Quality Tool - Integrated Frontend & Backend

## 🎯 Overview

This is a comprehensive leadership quality analysis tool that integrates:
- **React Frontend** (Next.js) - Modern UI for configuration and interaction
- **FastAPI Backend** - Robust API with Jira integration
- **Jira API Integration** - Real-time project management data analysis
- **AI Chat Interface** - Intelligent insights and recommendations

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**For Windows:**
```bash
start.bat
```

**For Linux/Mac:**
```bash
./start.sh
```

### Option 2: Manual Startup

1. **Start Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
   pip install -r requirements.txt
   python main.py
   ```

2. **Start Frontend (in a new terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🌐 Access Points

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🔧 Configuration

### Jira Integration Setup

1. **Get Jira Credentials:**
   - Jira URL: `https://your-domain.atlassian.net`
   - Email: Your Jira account email
   - API Token: Generate from [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Board ID: Found in your Jira board URL

2. **Configure in Frontend:**
   - Open http://localhost:3000
   - Go to "Jira Integration" tab
   - Enter your credentials
   - Test the connection
   - Save configuration

### Environment Variables (Optional)

Create a `.env` file in the project root:
```env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_BOARD_ID=123
OPENAI_API_KEY=your-openai-key
```

## 📊 Features

### 1. Jira Integration
- **Real-time Connection:** Live Jira API integration
- **Sprint Analysis:** Current sprint information and metrics
- **Issue Search:** Advanced JQL-based search capabilities
- **Status Monitoring:** Connection health and configuration status

### 2. AI Chat Interface
- **Intelligent Responses:** Context-aware AI assistance
- **Document Analysis:** Upload and analyze documents
- **Export Options:** PDF and PowerPoint export capabilities
- **Chat History:** Persistent conversation history

### 3. Leadership Insights
- **Sprint Velocity:** Track team performance over time
- **Workload Balance:** Analyze task distribution
- **Blocker Analysis:** Identify recurring impediments
- **Actionable Recommendations:** AI-powered suggestions

### 4. Document Analysis
- **Quick Upload:** Drag-and-drop document processing
- **Multiple Formats:** Support for PDF, DOCX, and more
- **AI Integration:** Document content analysis and insights

## 🔌 API Endpoints

### Jira Endpoints
- `POST /api/jira/configure` - Configure Jira connection
- `GET /api/jira/status` - Get connection status
- `POST /api/jira/test` - Test Jira connection
- `GET /api/jira/sprint/current` - Get current sprint info
- `POST /api/jira/search` - Search Jira issues

### Chat Endpoints
- `POST /api/chat` - Send chat message
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/clear` - Clear chat history

### Document Endpoints
- `POST /api/upload` - Upload document
- `GET /api/documents/status` - Get document status

### Export Endpoints
- `POST /api/export/pdf` - Export to PDF
- `POST /api/export/powerpoint` - Export to PowerPoint

## 🧪 Testing

Run the integration test:
```bash
python test_integration.py
```

This will test:
- Backend health
- Jira configuration
- API endpoints
- CORS headers
- Frontend-backend communication

## 🛠️ Troubleshooting

### Common Issues

1. **Backend won't start:**
   - Check if port 8000 is available
   - Ensure Python dependencies are installed
   - Check virtual environment activation

2. **Frontend won't start:**
   - Check if port 3000 is available
   - Ensure Node.js dependencies are installed
   - Clear npm cache: `npm cache clean --force`

3. **Jira connection fails:**
   - Verify Jira URL format (include https://)
   - Check API token validity
   - Ensure board ID is correct
   - Test connection in Jira directly

4. **CORS errors:**
   - Backend CORS is configured for localhost:3000
   - If using different ports, update CORS settings in `backend/main.py`

### Port Conflicts

If ports 8000 or 3000 are in use:
```bash
# Find processes using ports
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill processes
kill -9 <PID>  # Linux/Mac
taskkill /f /pid <PID>  # Windows
```

## 📁 Project Structure

```
Leadership Quality Tool/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API server
│   ├── requirements.txt    # Python dependencies
│   └── venv/               # Virtual environment
├── frontend/               # Next.js frontend
│   ├── app/                # App directory
│   │   ├── components/     # React components
│   │   ├── page.tsx        # Main page
│   │   └── layout.tsx      # App layout
│   ├── package.json        # Node dependencies
│   └── next.config.js      # Next.js config
├── src/                    # Source code
│   ├── jira_client.py      # Jira API client
│   ├── auth.py             # Authentication config
│   └── ...
├── start.sh               # Linux/Mac startup script
├── start.bat              # Windows startup script
├── test_integration.py    # Integration tests
└── README.md              # This file
```

## 🔒 Security Notes

- API tokens are stored in memory only (not persisted)
- CORS is configured for localhost only
- No sensitive data is logged
- Use HTTPS in production environments

## 🚀 Production Deployment

For production deployment:

1. **Environment Variables:** Set all required environment variables
2. **HTTPS:** Configure SSL certificates
3. **Database:** Replace in-memory storage with persistent database
4. **Authentication:** Implement proper user authentication
5. **Monitoring:** Add logging and monitoring
6. **Scaling:** Use production WSGI server (Gunicorn) and reverse proxy (Nginx)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run the integration test script
3. Check the API documentation at http://localhost:8000/docs
4. Review the console logs for error messages

## 🎉 Success!

Once everything is running:
- ✅ Frontend accessible at http://localhost:3000
- ✅ Backend API running at http://localhost:8000
- ✅ Jira integration configured and tested
- ✅ AI chat interface working
- ✅ Document upload and analysis functional

Your Leadership Quality Tool is now fully integrated and ready to provide insights into your team's performance and leadership patterns!
