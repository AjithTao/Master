# Leadership Quality Tool

A comprehensive AI-powered leadership management tool that integrates with Jira and Confluence to provide real-time insights, analytics, and intelligent recommendations for project management and team performance.

## 🚀 Quick Start

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
./start.sh
```

**Note:** The startup scripts are now in the root directory for easy access. They automatically call the main scripts from the `scripts/` folder.

## 📁 Project Structure

```
Leadership Quality Tool/
├── backend/                 # FastAPI backend application
│   ├── main.py             # Main API server
│   ├── intelligent_ai_engine.py  # AI engine with Jira integration
│   ├── jira_client.py       # Jira API client
│   ├── confluence_client.py # Confluence API client
│   ├── auth.py             # Authentication and configuration
│   ├── requirements.txt     # Python dependencies
│   └── venv/               # Virtual environment
├── frontend/               # Next.js frontend application
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── package.json        # Node.js dependencies
│   └── node_modules/      # Node.js packages
├── docs/                   # All documentation files
│   ├── README.md           # Original detailed README
│   ├── INTEGRATION_GUIDE.md # Setup and integration guide
│   ├── LEADERSHIP_USER_GUIDE.md # User manual
│   └── ...                 # Other documentation
├── tests/                  # Test files and debugging scripts
│   ├── test_integration.py # Integration tests
│   ├── test_ai.py          # AI engine tests
│   └── ...                 # Other test files
├── config/                 # Configuration files and templates
│   ├── config.env.template # Environment variables template
│   ├── jira_intents.json   # Jira integration intents
│   └── data/               # Training data and configurations
├── scripts/                # Startup and utility scripts
│   ├── start.bat           # Windows startup script
│   ├── start.sh            # Linux/Mac startup script
│   └── ...                 # Other utility scripts
├── archive/                # Old/unused files (preserved)
│   ├── src/                # Legacy source code
│   ├── images/              # Project images
│   └── ...                 # Other archived files
└── README.md              # This file
```

## 🌐 Access Points

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🔧 Configuration

### Environment Variables

Create a `backend/config.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token
```

### Jira Integration Setup

1. **Get Jira Credentials:**
   - Jira URL: `https://your-domain.atlassian.net`
   - Email: Your Jira account email
   - API Token: Generate from [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Board ID: Found in your Jira board URL

2. **Configure in Frontend:**
   - Open http://localhost:3000
   - Go to "Integration" tab
   - Enter your credentials
   - Test the connection
   - Save configuration

## 📊 Features

### 🤖 AI-Powered Chat Assistant
- Natural language query processing for Jira and Confluence
- Context-aware responses with follow-up question handling
- Intelligent JQL generation and entity extraction
- Leadership-style summaries and insights

### 📈 Leadership Analytics Dashboard
- Real-time project metrics and KPIs
- Sprint velocity tracking and trend analysis
- Team performance analytics
- AI-powered insights and projections

### 🔗 Integration Hub
- Jira API integration with comprehensive fallback mechanisms
- Confluence API integration for documentation search
- Secure authentication and configuration management
- Real-time connection status monitoring

### 📤 Export Capabilities
- Excel export for comprehensive data analysis
- PDF reports for leadership presentations
- PowerPoint presentations for stakeholder updates
- Real-time data export with filtering

## 🧪 Testing

Run tests from the `tests/` folder:

```bash
cd tests
python test_integration.py
python test_ai.py
```

## 📚 Documentation

All detailed documentation is available in the `docs/` folder:

- **[Integration Guide](docs/INTEGRATION_GUIDE.md)** - Complete setup and integration instructions
- **[User Guide](docs/LEADERSHIP_USER_GUIDE.md)** - Comprehensive user manual
- **[Setup Instructions](docs/GIT_SETUP_INSTRUCTIONS.md)** - Git and deployment setup
- **[AI Setup](docs/AI_SETUP_README.md)** - AI engine configuration
- **[Leadership Setup](docs/LEADERSHIP_SETUP.md)** - Leadership features setup

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.11+** - Core programming language
- **Jira REST API v3** - Primary integration with fallbacks to v2
- **Confluence REST API** - Documentation and knowledge base integration
- **OpenAI GPT-4o-mini** - AI-powered natural language processing

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI component library

## 🚀 Deployment

For deployment options, see the [Deployment Guide](docs/GIT_SETUP_INSTRUCTIONS.md) in the docs folder.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software developed by TAO Digital Solutions.

## 🆘 Support

For support and questions:
- Check the documentation in the `docs/` folder
- Review the test files in the `tests/` folder
- Contact the development team

---

**Powered by TAO Digital Solutions** 🚀
