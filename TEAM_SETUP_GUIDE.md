# 🚀 Leadership Quality Tool - Team Setup Guide

## 📋 Prerequisites

### Required Software:
1. **Git** - [Download here](https://git-scm.com/downloads)
2. **Python 3.8+** - [Download here](https://www.python.org/downloads/)
3. **Node.js 18+** - [Download here](https://nodejs.org/)
4. **Code Editor** - VS Code recommended

### Required Accounts:
1. **GitHub Account** - For accessing the repository
2. **OpenAI Account** - For AI functionality
3. **Jira Account** - For project management integration
4. **Confluence Account** - For documentation integration

## 🔧 Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/AjithTao/Master.git
cd Master
```

### Step 2: Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup
```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### Step 4: Configuration Setup

#### Backend Configuration:
1. **Copy the config template:**
   ```bash
   cp config.env.template config.env
   ```

2. **Edit `backend/config.env`:**
   ```env
   # Replace with your actual OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional settings
   OPENAI_MODEL=gpt-4o-mini
   DEBUG=false
   LOG_LEVEL=INFO
   ```

#### Frontend Configuration:
- No additional configuration needed for local development
- The app automatically detects local vs production environment

## 🚀 Running the Application

### Option 1: Using the Launcher Scripts (Recommended)

#### Windows:
```bash
# From project root directory
start.bat
```

#### Mac/Linux:
```bash
# From project root directory
./start.sh
```

### Option 2: Manual Startup

#### Terminal 1 - Backend:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

## 🌐 Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🔑 Required API Keys

### 1. OpenAI API Key
- **Get from:** https://platform.openai.com/api-keys
- **Cost:** Pay-per-use (very affordable for testing)
- **Usage:** Powers the AI chat and analysis features

### 2. Jira Credentials
- **Jira URL:** Your company's Jira instance URL
- **Email:** Your Jira account email
- **API Token:** Generate from Jira account settings

### 3. Confluence Credentials (Optional)
- **Confluence URL:** Your company's Confluence instance URL
- **Email:** Your Confluence account email
- **API Token:** Generate from Confluence account settings

## 🛠️ Team Configuration

### For Each Team Member:

1. **Get OpenAI API Key:**
   - Each member needs their own OpenAI account
   - Or use a shared team account (recommended for cost management)

2. **Get Jira Access:**
   - Each member needs access to the same Jira instance
   - Use their individual Jira credentials

3. **Update Config Files:**
   - Each member updates their own `backend/config.env`
   - Never commit API keys to Git

## 📁 Project Structure

```
Leadership Quality Tool/
├── backend/                 # Python FastAPI backend
│   ├── main.py            # Main application
│   ├── requirements.txt   # Python dependencies
│   ├── config.env        # Environment variables (create this)
│   └── ...
├── frontend/              # Next.js React frontend
│   ├── app/              # Application pages
│   ├── package.json      # Node.js dependencies
│   └── ...
├── scripts/              # Startup scripts
│   ├── start.bat        # Windows launcher
│   └── start.sh         # Mac/Linux launcher
├── start.bat            # Root launcher (Windows)
├── start.sh            # Root launcher (Mac/Linux)
└── README.md           # Project documentation
```

## 🔧 Troubleshooting

### Common Issues:

1. **Port Already in Use:**
   ```bash
   # Kill processes on ports 3000 and 8000
   # Windows:
   netstat -ano | findstr :3000
   taskkill /PID <PID_NUMBER> /F
   
   # Mac/Linux:
   lsof -ti:3000 | xargs kill -9
   ```

2. **Python Dependencies Issues:**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   pip install -r requirements.txt
   ```

3. **Node.js Dependencies Issues:**
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **API Connection Issues:**
   - Check if backend is running on port 8000
   - Verify OpenAI API key is correct
   - Check internet connection

## 🚀 Production Deployment

### For Production Use:
1. **Backend:** Deploy to Render/Railway/Heroku
2. **Frontend:** Deploy to Vercel/Netlify
3. **Environment Variables:** Set in deployment platform
4. **Custom Domain:** Configure in deployment platform

## 📞 Support

### Getting Help:
1. **Check logs:** Backend logs in terminal, Frontend logs in browser console
2. **GitHub Issues:** Create issues in the repository
3. **Team Chat:** Use your team communication channel

### Useful Commands:
```bash
# Check Python version
python --version

# Check Node.js version
node --version

# Check Git version
git --version

# Check if ports are free
netstat -an | findstr :3000  # Windows
lsof -i :3000                # Mac/Linux
```

## ✅ Verification Checklist

After setup, verify:
- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] API status shows "Online" (green dot)
- [ ] Can connect to Jira
- [ ] AI chat works
- [ ] Dashboard loads data

## 🎯 Next Steps

1. **Connect to Jira:** Use your Jira credentials
2. **Test AI Features:** Try asking questions about your projects
3. **Explore Dashboard:** Check project metrics and insights
4. **Configure Confluence:** Optional integration for documentation

---

**Happy coding! 🚀**

*For questions or issues, contact the development team.*
