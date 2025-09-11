"use client"

import React, { useState, useEffect } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Alert, AlertDescription, AlertTitle } from './ui/alert'
import { Badge } from './ui/badge'
import { 
  Crown, 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  Info,
  RefreshCw,
  Copy,
  Eye,
  EyeOff
} from 'lucide-react'

interface ServiceAccountConfig {
  email: string
  token: string
  url: string
}

interface LeadershipStatus {
  success: boolean
  leadership_access_available: boolean
  shared_service_account: boolean
  cached_data_available: boolean
  cache_valid: boolean
  last_cache_update: string | null
  message: string
}

export function LeadershipConfigCenter() {
  const [config, setConfig] = useState<ServiceAccountConfig>({
    email: '',
    token: '',
    url: ''
  })
  const [status, setStatus] = useState<LeadershipStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [showToken, setShowToken] = useState(false)
  const [testResult, setTestResult] = useState<string | null>(null)

  const checkStatus = async () => {
    try {
      const response = await fetch('/api/leadership/status')
      const data = await response.json()
      setStatus(data)
    } catch (error) {
      console.error('Failed to check leadership status:', error)
    }
  }

  const enableLeadershipAccess = async () => {
    try {
      setLoading(true)
      setTestResult(null)
      
      const response = await fetch('/api/leadership/enable', {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.success) {
        setTestResult(`✅ Success! Cached ${data.cached_projects} projects for leadership access.`)
        await checkStatus()
      } else {
        setTestResult(`❌ Failed: ${data.error}`)
      }
    } catch (error) {
      setTestResult(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const copyConfigTemplate = () => {
    const template = `# Add these to backend/config.env
JIRA_SHARED_EMAIL=${config.email || 'service-leadership@company.com'}
JIRA_SHARED_TOKEN=${config.token || 'your-service-account-api-token'}
JIRA_SHARED_URL=${config.url || 'https://company.atlassian.net'}`
    
    navigator.clipboard.writeText(template)
  }

  useEffect(() => {
    checkStatus()
  }, [])

  const getStatusBadge = () => {
    if (!status) return null

    if (status.shared_service_account) {
      return (
        <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
          <Shield className="w-3 h-3 mr-1" />
          Service Account Active
        </Badge>
      )
    } else if (status.cached_data_available) {
      return (
        <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">
          <CheckCircle className="w-3 h-3 mr-1" />
          Cached Data Available
        </Badge>
      )
    } else {
      return (
        <Badge variant="destructive" className="bg-red-100 text-red-800 border-red-200">
          <AlertTriangle className="w-3 h-3 mr-1" />
          Setup Required
        </Badge>
      )
    }
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Crown className="w-5 h-5 text-purple-600" />
            <CardTitle>Leadership Access Configuration</CardTitle>
          </div>
          {getStatusBadge()}
        </div>
        <CardDescription>
          Configure shared service account for leaders without individual Jira access
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Current Status */}
        {status && (
          <Alert className={status.leadership_access_available ? "border-green-200 bg-green-50" : "border-orange-200 bg-orange-50"}>
            <Info className="h-4 w-4" />
            <AlertTitle>Current Status</AlertTitle>
            <AlertDescription>
              {status.message}
              {status.last_cache_update && (
                <div className="mt-1 text-xs">
                  Last updated: {new Date(status.last_cache_update).toLocaleString()}
                </div>
              )}
            </AlertDescription>
          </Alert>
        )}

        {/* Configuration Form */}
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="service-email">Service Account Email</Label>
            <Input
              id="service-email"
              type="email"
              placeholder="service-leadership@company.com"
              value={config.email}
              onChange={(e) => setConfig(prev => ({ ...prev, email: e.target.value }))}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="service-token">API Token</Label>
            <div className="relative">
              <Input
                id="service-token"
                type={showToken ? "text" : "password"}
                placeholder="your-service-account-api-token"
                value={config.token}
                onChange={(e) => setConfig(prev => ({ ...prev, token: e.target.value }))}
                className="pr-10"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowToken(!showToken)}
              >
                {showToken ? (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-400" />
                )}
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="service-url">Jira URL</Label>
            <Input
              id="service-url"
              type="url"
              placeholder="https://company.atlassian.net"
              value={config.url}
              onChange={(e) => setConfig(prev => ({ ...prev, url: e.target.value }))}
            />
          </div>
        </div>

        {/* Instructions */}
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Setup Instructions</AlertTitle>
          <AlertDescription className="space-y-2">
            <p><strong>Step 1:</strong> Create a Jira service account with read-only permissions</p>
            <p><strong>Step 2:</strong> Generate an API token for the service account</p>
            <p><strong>Step 3:</strong> Add the configuration to your backend environment file:</p>
            <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-sm font-mono mt-2">
              <div className="flex justify-between items-start">
                <div>
                  # Add to backend/config.env<br/>
                  JIRA_SHARED_EMAIL={config.email || 'service-leadership@company.com'}<br/>
                  JIRA_SHARED_TOKEN={config.token || 'your-service-account-api-token'}<br/>
                  JIRA_SHARED_URL={config.url || 'https://company.atlassian.net'}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={copyConfigTemplate}
                  className="ml-2"
                >
                  <Copy className="w-3 h-3" />
                </Button>
              </div>
            </div>
            <p><strong>Step 4:</strong> Restart your backend server</p>
            <p><strong>Step 5:</strong> Click "Initialize Leadership Access" below</p>
          </AlertDescription>
        </Alert>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            onClick={enableLeadershipAccess}
            disabled={loading}
            className="flex items-center gap-2"
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Crown className="w-4 h-4" />
            )}
            {loading ? 'Initializing...' : 'Initialize Leadership Access'}
          </Button>
          
          <Button
            variant="outline"
            onClick={checkStatus}
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Status
          </Button>
        </div>

        {/* Test Result */}
        {testResult && (
          <Alert className={testResult.startsWith('✅') ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}>
            <AlertDescription>{testResult}</AlertDescription>
          </Alert>
        )}

        {/* Quick Access Commands */}
        <Alert className="border-blue-200 bg-blue-50">
          <Info className="h-4 w-4" />
          <AlertTitle>Quick Commands (for IT/Developers)</AlertTitle>
          <AlertDescription className="space-y-2">
            <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-sm font-mono">
              # Check status<br/>
              curl http://localhost:8000/api/leadership/status<br/><br/>
              
              # Initialize leadership access<br/>
              curl -X POST http://localhost:8000/api/leadership/enable<br/><br/>
              
              # Test leadership chat<br/>
              curl -X POST http://localhost:8000/api/leadership/chat \<br/>
              &nbsp;&nbsp;-H "Content-Type: application/json" \<br/>
              &nbsp;&nbsp;-d '{"{"}"message":"Give me an executive summary"{"}"}'
            </div>
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  )
}
