'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Settings, CheckCircle, XCircle, Clock, AlertCircle, RefreshCw } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface JiraStatus {
  configured: boolean
  url: string
  email: string
  board_id: string
}

export function Sidebar() {
  const router = useRouter()
  const [jiraStatus, setJiraStatus] = useState<JiraStatus>({
    configured: false,
    url: '',
    email: '',
    board_id: ''
  })
  const [confluenceConfigured, setConfluenceConfigured] = useState<boolean>(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    // Fetch Jira/Confluence status from API
    fetchStatuses()
    
    // Set up periodic refresh every 30 seconds
    const interval = setInterval(fetchStatuses, 30000)
    
    const handler = () => fetchStatuses()
    window.addEventListener('integration-update', handler as any)
    
    return () => {
      clearInterval(interval)
      window.removeEventListener('integration-update', handler as any)
    }
  }, [])

  const fetchStatuses = async () => {
    setIsRefreshing(true)
    try {
      const response = await fetch('http://localhost:8000/api/jira/status')
      const data = await response.json()
      
      // Update the status with the correct structure
      setJiraStatus({
        configured: data.configured || false,
        url: data.config?.url || '',
        email: data.config?.email || '',
        board_id: data.board_id || ''
      })
      // Confluence
      try {
        const confResp = await fetch('http://localhost:8000/api/confluence/status')
        const conf = await confResp.json()
        setConfluenceConfigured(!!conf.configured)
      } catch (e) {
        setConfluenceConfigured(false)
      }
    } catch (error) {
      console.error('Failed to fetch Jira status:', error)
      // Reset to default state on error
      setJiraStatus({
        configured: false,
        url: '',
        email: '',
        board_id: ''
      })
    } finally {
      setIsRefreshing(false)
    }
  }


  return (
    <aside className="h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-6 space-y-6 overflow-y-auto transition-colors duration-200">
      {/* Company Branding */}
      <div className="text-center p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-white">
        <h3 className="font-bold text-lg">TAO DIGITAL SOLUTIONS</h3>
        <p className="text-sm opacity-90">Integration Hub</p>
      </div>

      {/* Integration Status */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 dark:text-foreground">🔗 Integrations</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchStatuses}
            disabled={isRefreshing}
            className="p-1"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        
        {/* Jira Status */}
        <Card className="mb-4 cursor-pointer" onClick={() => router.push('/?tab=jira')}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4 text-gray-600 dark:text-muted-foreground" />
                <span className="font-medium">Jira</span>
              </div>
              <Badge variant={jiraStatus.configured ? "default" : "secondary"}>
                {isRefreshing ? (
                  <><RefreshCw className="w-3 h-3 mr-1 animate-spin" /> Refreshing...</>
                ) : jiraStatus.configured ? (
                  <><CheckCircle className="w-3 h-3 mr-1" /> Connected</>
                ) : (
                  <><XCircle className="w-3 h-3 mr-1" /> Not Connected</>
                )}
              </Badge>
            </div>
            <p className="text-sm text-gray-600 dark:text-muted-foreground">Project Management</p>
          </CardContent>
        </Card>

        {/* Confluence Status */}
        <Card className="mb-4 cursor-pointer" onClick={() => router.push('/?tab=confluence')}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4 text-gray-600 dark:text-muted-foreground" />
                <span className="font-medium">Confluence</span>
              </div>
              <Badge variant={confluenceConfigured ? 'default' : 'secondary'}>
                {confluenceConfigured ? 'Connected' : 'Configure'}
              </Badge>
            </div>
            <p className="text-sm text-gray-600 dark:text-muted-foreground">Knowledge Management</p>
          </CardContent>
        </Card>

        {/* GitHub Status */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4 text-gray-600 dark:text-muted-foreground" />
                <span className="font-medium">GitHub</span>
              </div>
              <Badge variant="secondary">
                <Clock className="w-3 h-3 mr-1" /> Coming Soon
              </Badge>
            </div>
            <p className="text-sm text-gray-600 dark:text-muted-foreground">Code Repository</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="font-semibold text-gray-900 dark:text-foreground mb-4">⚡ Quick Actions</h3>
        <div className="space-y-2">
          <Button variant="outline" className="w-full justify-between" disabled>
            <span>📊 Sprint Analytics</span>
            <span className="text-xs text-gray-500">Coming soon</span>
          </Button>
          <Button variant="outline" className="w-full justify-between" disabled>
            <span>🔍 QA Metrics</span>
            <span className="text-xs text-gray-500">Coming soon</span>
          </Button>
          <Button variant="outline" className="w-full justify-between" disabled>
            <span>📈 Team Performance</span>
            <span className="text-xs text-gray-500">Coming soon</span>
          </Button>
        </div>
      </div>

      {/* Footer */}
      <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
        <p className="text-center text-xs text-gray-500 dark:text-muted-foreground">
          Powered by TAO Digital Solutions
        </p>
      </div>
    </aside>
  )
}
