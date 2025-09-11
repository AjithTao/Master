"use client"

import React, { useState, useEffect } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Alert, AlertDescription, AlertTitle } from './ui/alert'
import { Badge } from './ui/badge'
import { 
  FileText, 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  Settings,
  RefreshCw,
  Eye,
  EyeOff,
  Zap,
  ChevronDown,
  ChevronUp,
  BookOpen
} from 'lucide-react'

interface ConfluenceConfig {
  url: string
  email: string
  apiToken: string
}

interface ConfluenceStatus {
  success: boolean
  configured: boolean
  message: string
  spaces?: number
  testResult?: string
}

export function SimpleConfluenceConnect() {
  const [status, setStatus] = useState<ConfluenceStatus | null>(null)
  const [config, setConfig] = useState<ConfluenceConfig>({
    url: '',
    email: '',
    apiToken: ''
  })
  const [loading, setLoading] = useState(false)
  const [showManualEntry, setShowManualEntry] = useState(false)
  const [showToken, setShowToken] = useState(false)
  const [savedConfig, setSavedConfig] = useState<ConfluenceConfig | null>(null)
  const [connectionResult, setConnectionResult] = useState<string | null>(null)

  // Load saved configuration from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('confluence_config')
    if (saved) {
      try {
        const parsedConfig = JSON.parse(saved)
        setSavedConfig(parsedConfig)
        setConfig(parsedConfig)
      } catch (error) {
        console.error('Failed to load saved Confluence config:', error)
      }
    }
  }, [])

  // Check current status
  const checkStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/confluence/status')
      const data = await response.json()
      setStatus(data)
      return data
    } catch (error) {
      console.error('Failed to check Confluence status:', error)
      setStatus({
        success: false,
        configured: false,
        message: 'Failed to check status'
      })
      return null
    }
  }

  // Save configuration to localStorage
  const saveConfiguration = async () => {
    try {
      // Save to localStorage
      localStorage.setItem('confluence_config', JSON.stringify(config))
      setSavedConfig(config)
      return true
    } catch (error) {
      console.error('Failed to save Confluence configuration:', error)
      return false
    }
  }

  // One-click connect
  const handleConnect = async () => {
    try {
      setLoading(true)
      setConnectionResult(null)
      
      // Check if we have saved configuration
      if (!savedConfig || !savedConfig.url || !savedConfig.email || !savedConfig.apiToken) {
        setConnectionResult("❌ No saved connection details found. Please enter connection details first.")
        setShowManualEntry(true)
        return
      }
      
      // Try to connect using saved configuration
      const response = await fetch('http://localhost:8000/api/confluence/configure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: savedConfig.url,
          email: savedConfig.email,
          api_token: savedConfig.apiToken
        }),
      })
      
      const data = await response.json()
      
      if (data.success) {
        setConnectionResult(`✅ Connected successfully! ${data.test_result || 'Confluence connection verified.'}`)
        await checkStatus()
      } else {
        setConnectionResult(`❌ Connection failed: ${data.error || data.message}. Please check your connection details.`)
        setShowManualEntry(true)
      }
    } catch (error) {
      console.error('Connection error:', error)
      // Handle JSON parsing errors
      if (error instanceof SyntaxError && error.message.includes('JSON')) {
        setConnectionResult("❌ Server returned invalid response. Please check if the backend server is running.")
      } else {
        setConnectionResult(`❌ Connection error: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
      setShowManualEntry(true)
    } finally {
      setLoading(false)
    }
  }

  // Save and connect with manual details
  const handleSaveAndConnect = async () => {
    try {
      setLoading(true)
      setConnectionResult(null)
      
      // Validate inputs
      if (!config.url || !config.email || !config.apiToken) {
        setConnectionResult("❌ Please fill in URL, email, and API token.")
        return
      }
      
      // Validate URL format
      if (!config.url.includes('atlassian.net')) {
        setConnectionResult("❌ URL should be your Atlassian domain (e.g., company.atlassian.net)")
        return
      }
      
      // Save configuration
      const saved = await saveConfiguration()
      if (!saved) {
        setConnectionResult("❌ Failed to save configuration.")
        return
      }
      
      setConnectionResult("✅ Configuration saved! Now attempting connection...")
      
      // Wait a moment then try to connect
      setTimeout(async () => {
        await handleConnect()
        setShowManualEntry(false)
      }, 1000)
      
    } catch (error) {
      setConnectionResult(`❌ Save error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  // Initial status check
  useEffect(() => {
    checkStatus()
  }, [])

  const getStatusBadge = () => {
    if (!status) return null

    if (status.configured) {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-green-100 dark:bg-green-900/30 rounded-full">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-green-700 dark:text-green-400 text-sm font-medium">Connected</span>
        </div>
      )
    } else {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-full">
          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
          <span className="text-gray-600 dark:text-gray-400 text-sm font-medium">Not Connected</span>
        </div>
      )
    }
  }

  return (
    <Card className="h-full shadow-lg border-0 bg-gradient-to-br from-white/80 to-green-50/50 dark:from-gray-800 dark:to-green-900/20 backdrop-blur-sm">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <FileText className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <CardTitle className="text-xl">Confluence Integration</CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Connect to Confluence for documentation and knowledge base insights
              </p>
            </div>
          </div>
          {getStatusBadge()}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Main Connect Button */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <Button
            onClick={handleConnect}
            disabled={loading}
            size="lg"
            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            {loading ? 'Connecting...' : 'Connect to Confluence'}
          </Button>

          {/* Manual Entry Toggle */}
          <Button
            variant="outline"
            onClick={() => setShowManualEntry(!showManualEntry)}
            className="flex items-center gap-2 border-gray-300 hover:border-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-all duration-200"
          >
            <Settings className="w-4 h-4" />
            Enter Connection Details
            {showManualEntry ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
        </div>


        {/* Connection Result */}
        {connectionResult && (
          <Alert className={connectionResult.startsWith('✅') ? 
            "border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20" : 
            "border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20"
          }>
            <AlertDescription className={connectionResult.startsWith('✅') ? 
              "text-green-700 dark:text-green-300" : 
              "text-red-700 dark:text-red-300"
            }>
              {connectionResult}
            </AlertDescription>
          </Alert>
        )}

        {/* Manual Entry Form */}
        {showManualEntry && (
          <div className="space-y-4 border-t border-gray-200 dark:border-gray-700 pt-4">
            <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300">Confluence Connection Details</h4>
            
            {/* Saved Configuration Display */}
            {savedConfig && (
              <div className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-start gap-3">
                  <div className="p-1 bg-green-100 dark:bg-green-900/40 rounded-full">
                    <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="flex-1">
                    <h5 className="font-semibold text-green-800 dark:text-green-200 mb-1 text-sm">Saved Configuration Found</h5>
                    <p className="text-xs text-green-700 dark:text-green-300">
                      Ready to connect as: <span className="font-medium">{savedConfig.email}</span>
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1 font-mono">
                      {savedConfig.url}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="space-y-3">
              <div className="space-y-1">
                <Label htmlFor="confluence-url" className="text-xs text-gray-600 dark:text-gray-400">Confluence URL</Label>
                <Input
                  id="confluence-url"
                  type="url"
                  placeholder="https://company.atlassian.net/wiki"
                  value={config.url}
                  onChange={(e) => setConfig(prev => ({ ...prev, url: e.target.value }))}
                  className="text-sm"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="confluence-email" className="text-xs text-gray-600 dark:text-gray-400">Email</Label>
                <Input
                  id="confluence-email"
                  type="email"
                  placeholder="your.email@company.com"
                  value={config.email}
                  onChange={(e) => setConfig(prev => ({ ...prev, email: e.target.value }))}
                  className="text-sm"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="confluence-token" className="text-xs text-gray-600 dark:text-gray-400">API Token</Label>
                <div className="relative">
                  <Input
                    id="confluence-token"
                    type={showToken ? "text" : "password"}
                    placeholder="your-confluence-api-token"
                    value={config.apiToken}
                    onChange={(e) => setConfig(prev => ({ ...prev, apiToken: e.target.value }))}
                    className="text-sm pr-8"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-2 hover:bg-transparent"
                    onClick={() => setShowToken(!showToken)}
                  >
                    {showToken ? (
                      <EyeOff className="h-3 w-3 text-gray-400 dark:text-gray-500" />
                    ) : (
                      <Eye className="h-3 w-3 text-gray-400 dark:text-gray-500" />
                    )}
                  </Button>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleSaveAndConnect}
                disabled={loading}
                className="flex items-center gap-2"
              >
                {loading ? (
                  <RefreshCw className="w-3 h-3 animate-spin" />
                ) : (
                  <CheckCircle className="w-3 h-3" />
                )}
                Save & Connect
              </Button>
              
              <Button
                variant="outline"
                onClick={() => setShowManualEntry(false)}
                disabled={loading}
              >
                Cancel
              </Button>
            </div>

            {/* Help Information */}
            <Alert className="border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20">
              <BookOpen className="h-4 w-4 text-green-600 dark:text-green-400" />
              <AlertTitle className="text-green-800 dark:text-green-200">How to get your API Token</AlertTitle>
              <AlertDescription className="space-y-2 text-xs text-green-700 dark:text-green-300">
                <p>1. Go to <strong>Atlassian Account Settings</strong></p>
                <p>2. Click <strong>Security</strong> → <strong>Create and manage API tokens</strong></p>
                <p>3. Click <strong>Create API token</strong></p>
                <p>4. Give it a name like "Confluence Access"</p>
                <p>5. Copy the token and paste it above</p>
                <p><strong>Note:</strong> Same token can be used for both Jira and Confluence</p>
              </AlertDescription>
            </Alert>
          </div>
        )}

        {/* Quick Status */}
        {status && (
          <div className="text-xs text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-3">
            <div className="flex justify-between items-center">
              <span>Status:</span>
              <span className="font-medium">{status.message}</span>
            </div>
            {status.testResult && (
              <div className="flex justify-between items-center mt-1">
                <span>Test Result:</span>
                <span>{status.testResult}</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
