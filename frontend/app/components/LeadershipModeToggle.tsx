"use client"

import React, { useState, useEffect } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Alert, AlertDescription, AlertTitle } from './ui/alert'
import { 
  Crown, 
  Shield, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  Settings,
  RefreshCw,
  Users,
  Info
} from 'lucide-react'

interface LeadershipStatus {
  success: boolean
  leadership_access_available: boolean
  shared_service_account: boolean
  cached_data_available: boolean
  cache_valid: boolean
  last_cache_update: string | null
  message: string
  error?: string
}

interface LeadershipModeToggleProps {
  onModeChange: (isLeadershipMode: boolean, status?: LeadershipStatus) => void
  isLeadershipMode: boolean
}

export default function LeadershipModeToggle({ 
  onModeChange, 
  isLeadershipMode 
}: LeadershipModeToggleProps) {
  const [status, setStatus] = useState<LeadershipStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [showSetup, setShowSetup] = useState(false)

  const checkLeadershipStatus = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/leadership/status')
      const data = await response.json()
      setStatus(data)
      return data
    } catch (error) {
      console.error('Failed to check leadership status:', error)
      setStatus({
        success: false,
        leadership_access_available: false,
        shared_service_account: false,
        cached_data_available: false,
        cache_valid: false,
        last_cache_update: null,
        message: 'Failed to check status',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
      return null
    } finally {
      setLoading(false)
    }
  }

  const enableLeadershipAccess = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/leadership/enable', {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.success) {
        // Refresh status after enabling
        await checkLeadershipStatus()
      }
      
      return data
    } catch (error) {
      console.error('Failed to enable leadership access:', error)
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' }
    } finally {
      setLoading(false)
    }
  }

  const handleToggleLeadershipMode = async () => {
    if (!isLeadershipMode) {
      // Enabling leadership mode - check status first
      const currentStatus = await checkLeadershipStatus()
      
      if (currentStatus?.leadership_access_available) {
        onModeChange(true, currentStatus)
      } else {
        setShowSetup(true)
      }
    } else {
      // Disabling leadership mode
      onModeChange(false)
    }
  }

  const formatLastUpdate = (timestamp: string | null) => {
    if (!timestamp) return 'Never'
    
    try {
      const date = new Date(timestamp)
      const now = new Date()
      const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
      
      if (diffMinutes < 60) {
        return `${diffMinutes} minutes ago`
      } else if (diffMinutes < 24 * 60) {
        const hours = Math.floor(diffMinutes / 60)
        return `${hours} hour${hours > 1 ? 's' : ''} ago`
      } else {
        return date.toLocaleDateString()
      }
    } catch {
      return 'Unknown'
    }
  }

  useEffect(() => {
    if (isLeadershipMode) {
      checkLeadershipStatus()
    }
  }, [isLeadershipMode])

  const getStatusBadge = () => {
    if (!status) return null

    if (status.shared_service_account) {
      return (
        <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
          <Shield className="w-3 h-3 mr-1" />
          Live Data
        </Badge>
      )
    } else if (status.cached_data_available && status.cache_valid) {
      return (
        <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">
          <Clock className="w-3 h-3 mr-1" />
          Cached Data
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
    <div className="space-y-4">
      {/* Main Toggle Button */}
      <div className="flex items-center gap-3">
        <Button
          onClick={handleToggleLeadershipMode}
          variant={isLeadershipMode ? "default" : "outline"}
          className={`flex items-center gap-2 ${
            isLeadershipMode 
              ? "bg-purple-600 hover:bg-purple-700 text-white" 
              : "border-purple-200 hover:bg-purple-50"
          }`}
          disabled={loading}
        >
          {loading ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Crown className="w-4 h-4" />
          )}
          {isLeadershipMode ? "Leadership Mode ON" : "Enable Leadership Mode"}
        </Button>
        
        {status && getStatusBadge()}
      </div>

      {/* Status Information (when in leadership mode) */}
      {isLeadershipMode && status && (
        <Card className="border-purple-200">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm">
              <Users className="w-4 h-4" />
              Leadership Access Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                {status.shared_service_account ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-orange-500" />
                )}
                <span>
                  {status.shared_service_account ? "Live Data Access" : "No Live Access"}
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                {status.cached_data_available ? (
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-orange-500" />
                )}
                <span>
                  {status.cached_data_available ? "Cached Data Available" : "No Cached Data"}
                </span>
              </div>
            </div>

            {status.last_cache_update && (
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Clock className="w-3 h-3" />
                Last updated: {formatLastUpdate(status.last_cache_update)}
              </div>
            )}

            <div className="text-xs text-gray-500">
              {status.message}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Setup Instructions Modal */}
      {showSetup && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-800">
              <Settings className="w-5 h-5" />
              Leadership Access Setup Required
            </CardTitle>
            <CardDescription>
              Leadership mode needs to be configured by your IT administrator
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>For IT Administrator</AlertTitle>
              <AlertDescription className="space-y-2">
                <p>To enable leadership access, configure the shared service account:</p>
                <div className="bg-gray-100 p-3 rounded text-sm font-mono">
                  # Add to backend/config.env<br/>
                  JIRA_SHARED_EMAIL=service-account@company.com<br/>
                  JIRA_SHARED_TOKEN=your-service-account-token<br/>
                  JIRA_SHARED_URL=https://company.atlassian.net
                </div>
                <p>Then run: <code className="bg-gray-200 px-1 rounded">curl -X POST /api/leadership/enable</code></p>
              </AlertDescription>
            </Alert>

            <Alert className="border-blue-200 bg-blue-50">
              <Users className="h-4 w-4" />
              <AlertTitle>For Leaders</AlertTitle>
              <AlertDescription>
                Contact your IT team with this message: <br/>
                <em>"Please enable leadership access for the Quality Tool using the shared service account setup."</em>
              </AlertDescription>
            </Alert>

            <div className="flex gap-2">
              <Button
                onClick={enableLeadershipAccess}
                variant="outline"
                size="sm"
                disabled={loading}
              >
                {loading && <RefreshCw className="w-3 h-3 mr-1 animate-spin" />}
                Try Enable Now
              </Button>
              
              <Button
                onClick={() => setShowSetup(false)}
                variant="ghost"
                size="sm"
              >
                Close
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions (when in leadership mode and working) */}
      {isLeadershipMode && status?.leadership_access_available && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-green-800">Quick Leadership Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2">
              <Button 
                variant="outline" 
                size="sm"
                className="text-xs"
                onClick={() => {
                  // This would trigger a chat message
                  // You can integrate this with your chat system
                  console.log('Portfolio overview requested')
                }}
              >
                Portfolio Overview
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className="text-xs"
                onClick={() => {
                  console.log('Team capacity requested')
                }}
              >
                Team Capacity
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className="text-xs"
                onClick={() => {
                  console.log('Project health requested')
                }}
              >
                Project Health
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className="text-xs"
                onClick={() => {
                  console.log('Key metrics requested')
                }}
              >
                Key Metrics
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
