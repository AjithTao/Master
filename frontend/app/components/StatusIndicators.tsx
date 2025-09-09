'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { CheckCircle, XCircle, Clock, AlertCircle, RefreshCw } from 'lucide-react'

interface SystemStatus {
  jira: {
    configured: boolean
    connected: boolean
    lastSync?: string
  }
  confluence: {
    configured: boolean
  }
  api: {
    status: 'online' | 'offline' | 'error'
  }
}

export function StatusIndicators() {
  const [status, setStatus] = useState<SystemStatus>({
    jira: { configured: false, connected: false },
    confluence: { configured: false },
    api: { status: 'offline' }
  })
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string>('')

  useEffect(() => {
    fetchStatus()
    // Set up periodic refresh
    const interval = setInterval(fetchStatus, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const handler = () => fetchStatus()
    window.addEventListener('integration-update', handler as any)
    return () => window.removeEventListener('integration-update', handler as any)
  }, [])

  const fetchStatus = async () => {
    try {
      // Fetch Jira status
      const jiraResponse = await fetch('http://localhost:8000/api/jira/status')
      const jiraData = await jiraResponse.json()
      // Fetch Confluence status
      const confResponse = await fetch('http://localhost:8000/api/confluence/status')
      const confData = await confResponse.json()
      
      setStatus({
        jira: {
          configured: jiraData.configured,
          connected: jiraData.configured, // Assume connected if configured
          lastSync: jiraData.configured ? new Date().toISOString() : undefined
        },
        confluence: {
          configured: !!confData.configured
        },
        api: { status: 'online' }
      })
      
      // Update the last updated time
      setLastUpdated(new Date().toLocaleTimeString())
    } catch (error) {
      setStatus(prev => ({
        ...prev,
        api: { status: 'error' }
      }))
    }
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await fetchStatus()
    setIsRefreshing(false)
  }

  const getStatusIcon = (status: boolean | string) => {
    if (typeof status === 'boolean') {
      return status ? (
        <CheckCircle className="w-4 h-4 text-green-600" />
      ) : (
        <XCircle className="w-4 h-4 text-red-600" />
      )
    }
    
    switch (status) {
      case 'online':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'offline':
        return <XCircle className="w-4 h-4 text-red-600" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-yellow-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status: boolean | string) => {
    if (typeof status === 'boolean') {
      return (
        <Badge variant={status ? "default" : "secondary"}>
          {status ? 'Active' : 'Inactive'}
        </Badge>
      )
    }
    
    switch (status) {
      case 'online':
        return <Badge variant="default">Online</Badge>
      case 'offline':
        return <Badge variant="secondary">Offline</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>System Status</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
        <CardDescription>
          Current status of all integrated services
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Jira Status */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-card border border-gray-200 dark:border-border rounded-lg">
          <div className="flex items-center space-x-3">
            {getStatusIcon(status.jira.configured)}
            <div>
              <p className="font-medium text-sm">Jira Integration</p>
              <p className="text-xs text-gray-600 dark:text-muted-foreground">
                {status.jira.configured ? 'Project Management' : 'Not Configured'}
              </p>
            </div>
          </div>
          {getStatusBadge(status.jira.configured)}
        </div>

        {/* Confluence Status */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-card border border-gray-200 dark:border-border rounded-lg">
          <div className="flex items-center space-x-3">
            {getStatusIcon(status.confluence.configured)}
            <div>
              <p className="font-medium text-sm">Confluence Integration</p>
              <p className="text-xs text-gray-600 dark:text-muted-foreground">
                {status.confluence.configured ? 'Knowledge Management' : 'Not Configured'}
              </p>
            </div>
          </div>
          {getStatusBadge(status.confluence.configured)}
        </div>

        {/* API Status */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-card border border-gray-200 dark:border-border rounded-lg">
          <div className="flex items-center space-x-3">
            {getStatusIcon(status.api.status)}
            <div>
              <p className="font-medium text-sm">API Service</p>
              <p className="text-xs text-gray-600 dark:text-muted-foreground">
                {status.api.status === 'online' ? 'All systems operational' : 'Service unavailable'}
              </p>
            </div>
          </div>
          {getStatusBadge(status.api.status)}
        </div>

        {/* Last Updated */}
        <div className="text-xs text-gray-500 dark:text-muted-foreground text-center pt-2 border-t border-gray-200 dark:border-border">
          Last updated: {lastUpdated || 'Loading...'}
        </div>
      </CardContent>
    </Card>
  )
}
