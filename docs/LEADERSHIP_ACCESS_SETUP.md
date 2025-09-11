# 🎯 Leadership Access Setup Guide

## Overview

This guide enables **leaders and executives without Jira access** to view insights and analytics through the Leadership Quality Tool. No individual API tokens required!

## 🚀 Quick Setup Options

### Option 1: Shared Service Account (Recommended)

**Best for**: Production environments, multiple leaders, real-time data

1. **Create Jira Service Account**:
   - Create a dedicated Jira user: `service-leadership@company.com`
   - Generate API token for this account
   - Grant **read-only** permissions to relevant projects

2. **Configure Backend**:
   ```bash
   # Add to backend/config.env
   JIRA_SHARED_EMAIL=service-leadership@company.com
   JIRA_SHARED_TOKEN=your-service-account-api-token
   JIRA_SHARED_URL=https://your-company.atlassian.net
   ```

3. **Enable Leadership Access**:
   ```bash
   curl -X POST http://localhost:8000/api/leadership/enable
   ```

### Option 2: Cached Data Mode (Fallback)

**Best for**: Demo environments, offline access, when service accounts aren't available

1. **Initial Setup** (requires one-time Jira access):
   - Someone with Jira access configures the system normally
   - System caches analytics data automatically
   - Cache refreshes every 4 hours (configurable)

2. **Leaders Access Cached Data**:
   - No individual tokens needed
   - Data updates periodically
   - Perfect for executive dashboards

## 🔧 API Endpoints for Leadership Access

### Check Status
```bash
GET /api/leadership/status
# Returns: availability, cache status, configuration info
```

### Get Executive Summary
```bash
GET /api/leadership/summary
# Returns: high-level portfolio overview without needing Jira tokens
```

### Leadership Chat
```bash
POST /api/leadership/chat
Content-Type: application/json
{
  "message": "Show me project status overview"
}
# Works like regular chat but uses shared/cached data
```

## 🎯 Frontend Integration

### Leadership Mode Toggle

Add to your frontend a "Leadership Mode" that:
1. Uses `/api/leadership/chat` instead of `/api/chat`
2. Shows data source (live vs cached)
3. Displays last update timestamp
4. Provides setup instructions if not configured

### Example Implementation

```typescript
// Check if leadership access is available
const checkLeadershipAccess = async () => {
  const response = await fetch('/api/leadership/status');
  const status = await response.json();
  
  if (status.leadership_access_available) {
    // Enable leadership mode
    setLeadershipMode(true);
  } else {
    // Show setup instructions
    showSetupInstructions(status);
  }
};

// Use leadership chat
const sendLeadershipQuery = async (message: string) => {
  const response = await fetch('/api/leadership/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  
  const result = await response.json();
  
  // Show data source indicator
  const dataSource = result.data_source; // 'live_jira_data' or 'cached_analytics'
  const lastUpdated = result.last_updated;
  
  return result.response;
};
```

## 🛡️ Security Considerations

### Shared Service Account Security
- **Read-only permissions only**
- **Project-level access control** (limit to relevant projects)
- **Regular token rotation** (quarterly recommended)
- **Audit trail monitoring** (track service account usage)

### Data Privacy
- **Cached data encryption** (sensitive project info)
- **Access logging** (track who views what)
- **Data retention policies** (auto-expire old cache)

## 📊 What Leaders Can Access

### ✅ Available Features
- **Project health overviews**
- **Team workload distribution**
- **Completion rates and trends**
- **High-level portfolio metrics**
- **Strategic insights and recommendations**

### ❌ Restricted Features
- **Individual ticket details** (privacy)
- **Personal assignee performance** (HR sensitive)
- **Detailed technical discussions** (comments, descriptions)
- **Administrative functions** (no data modification)

## 🎯 Example Leadership Queries

```bash
# Portfolio overview
"Show me our project portfolio status"

# Team insights
"Which projects need more attention?"

# Performance metrics
"How are our completion rates?"

# Resource planning
"What's our current team capacity?"

# Strategic analysis
"Compare CCM and TI project progress"
```

## 🚨 Troubleshooting

### "Leadership access not configured"
- Check environment variables are set
- Verify service account has proper permissions
- Call `/api/leadership/enable` to initialize

### "No cached data available"
- Service account needs to be configured first
- Cache refresh may be in progress
- Check `/api/leadership/status` for details

### "Data seems outdated"
- Cached data refreshes every 4 hours
- Force refresh with `/api/leadership/enable`
- Consider switching to shared service account for real-time data

## 🎉 Benefits

### For Leaders
- **No Jira training required**
- **Executive-focused insights**
- **Always available access**
- **Mobile-friendly summaries**

### For IT Teams
- **Reduced license costs** (no individual Jira seats)
- **Centralized access control**
- **Audit compliance**
- **Simplified user management**

### For Organizations
- **Better leadership visibility**
- **Data-driven decisions**
- **Improved project governance**
- **Enhanced strategic planning**

---

**Ready to enable leadership access? Start with Option 1 (Shared Service Account) for the best experience!** 🚀
