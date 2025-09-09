'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Alert, AlertDescription } from './ui/alert'
import { CheckCircle, XCircle, Loader2, Settings } from 'lucide-react'

interface JiraConfig {
  url: string
  email: string
  api_token: string
  board_id: string
}

export function JiraConfigCenter() {
  const [config, setConfig] = useState<JiraConfig>({
    url: '',
    email: '',
    api_token: '',
    board_id: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')
  const [showConfig, setShowConfig] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [currentConfig, setCurrentConfig] = useState<JiraConfig | null>(null)

  const handleConfigChange = (field: keyof JiraConfig, value: string) => {
    setConfig(prev => ({ ...prev, [field]: value }))
  }

  // Check connection status on component mount
  useEffect(() => {
    checkConnectionStatus()
  }, [])

  const checkConnectionStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jira/status')
      const data = await response.json()
      
      if (data.configured && data.config) {
        setIsConnected(true)
        setCurrentConfig({
          url: data.config.url || '',
          email: data.config.email || '',
          api_token: '••••••••', // Hide the token
          board_id: data.board_id || ''
        })
      } else {
        setIsConnected(false)
        setCurrentConfig(null)
      }
    } catch (error) {
      console.error('Failed to check connection status:', error)
      setIsConnected(false)
      setCurrentConfig(null)
    }
  }

  const handleSaveConfig = async () => {
    setIsLoading(true)
    setStatus('idle')
    
    try {
      const response = await fetch('http://localhost:8000/api/jira/configure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setStatus('success')
        setMessage('Jira configured successfully!')
        setShowConfig(false)
        setIsConnected(true)
        setCurrentConfig({
          url: config.url,
          email: config.email,
          api_token: '••••••••',
          board_id: config.board_id
        })
        // Refresh connection status
        checkConnectionStatus()
      } else {
        setStatus('error')
        setMessage(data.detail || 'Configuration failed')
      }
    } catch (error) {
      setStatus('error')
      setMessage('Network error: ' + error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestConnection = async () => {
    setIsLoading(true)
    setStatus('idle')
    
    try {
      const response = await fetch('http://localhost:8000/api/jira/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        setStatus('success')
        setMessage(data.message || 'Connection test successful!')
      } else {
        setStatus('error')
        setMessage(data.message || data.detail || 'Connection test failed')
      }
    } catch (error) {
      setStatus('error')
      setMessage('Network error: ' + error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDisconnect = async () => {
    setIsLoading(true)
    setStatus('idle')
    
    try {
      // Clear the backend configuration
      const response = await fetch('http://localhost:8000/api/jira/disconnect', {
        method: 'POST'
      })
      
      if (response.ok) {
        setStatus('success')
        setMessage('Jira disconnected successfully!')
        setIsConnected(false)
        setCurrentConfig(null)
        setShowConfig(false)
      } else {
        setStatus('error')
        setMessage('Failed to disconnect')
      }
    } catch (error) {
      setStatus('error')
      setMessage('Network error: ' + error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Settings className="w-5 h-5" />
          <span>Jira Configuration</span>
        </CardTitle>
        <CardDescription>
          Connect your Jira instance to enable project management and analytics features
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {!showConfig ? (
          isConnected ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Jira Connected</h3>
              <p className="text-gray-600 dark:text-muted-foreground mb-4">
                Connected to {currentConfig?.url}
              </p>
              <div className="bg-gray-50 dark:bg-card p-4 rounded-lg mb-6 text-left border border-gray-200 dark:border-border">
                <p className="text-sm"><strong>Email:</strong> {currentConfig?.email}</p>
                <p className="text-sm"><strong>Board ID:</strong> {currentConfig?.board_id}</p>
              </div>
              <div className="flex">
                <Button 
                  onClick={handleDisconnect} 
                  variant="outline" 
                  className="w-full"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : null}
                  Disconnect
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gray-100 dark:bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                <Settings className="w-8 h-8 text-gray-400 dark:text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Configure Jira Integration</h3>
              <p className="text-gray-600 dark:text-muted-foreground mb-6">
                Set up your Jira connection to unlock powerful project management and analytics features
              </p>
              <Button onClick={() => setShowConfig(true)} className="w-full">
                Configure Jira
              </Button>
            </div>
          )
        ) : (
          <div className="space-y-4">
            {/* Status Alert */}
            {status !== 'idle' && (
              <Alert variant={status === 'success' ? 'default' : 'destructive'}>
                {status === 'success' ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <XCircle className="h-4 w-4" />
                )}
                <AlertDescription>{message}</AlertDescription>
              </Alert>
            )}

            {/* Configuration Form */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="jira-url">Jira URL</Label>
                <Input
                  id="jira-url"
                  type="url"
                  placeholder="https://your-domain.atlassian.net"
                  value={config.url}
                  onChange={(e) => handleConfigChange('url', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="jira-email">Email</Label>
                <Input
                  id="jira-email"
                  type="email"
                  placeholder="your-email@example.com"
                  value={config.email}
                  onChange={(e) => handleConfigChange('email', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="jira-token">API Token</Label>
                <Input
                  id="jira-token"
                  type="password"
                  placeholder="your-api-token"
                  value={config.api_token}
                  onChange={(e) => handleConfigChange('api_token', e.target.value)}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Get your API token from{' '}
                  <a 
                    href="https://id.atlassian.com/manage-profile/security/api-tokens" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Atlassian Account Settings
                  </a>
                </p>
              </div>
              
              <div>
                <Label htmlFor="jira-board">Board ID (Optional)</Label>
                <Input
                  id="jira-board"
                  type="text"
                  placeholder="123"
                  value={config.board_id}
                  onChange={(e) => handleConfigChange('board_id', e.target.value)}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Find this in your Jira board URL
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <Button 
                onClick={handleSaveConfig} 
                disabled={isLoading || !config.url || !config.email || !config.api_token}
                className="flex-1"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : null}
                Save & Connect
              </Button>
              
              <Button 
                variant="outline" 
                onClick={() => setShowConfig(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
            </div>

            {/* Test Connection Button */}
            {config.url && config.email && config.api_token && (
              <Button 
                variant="outline" 
                onClick={handleTestConnection}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : null}
                Test Connection
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
