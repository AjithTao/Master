"use client"

import React, { useState, useEffect } from 'react'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Alert, AlertDescription, AlertTitle } from './ui/alert'
import { 
  Crown, 
  Shield, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  Info,
  RefreshCw,
  Settings
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

export default function LeadershipStatusIndicator() {
  const [status, setStatus] = useState<LeadershipStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

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
    checkLeadershipStatus()
  }, [])

  const getStatusBadge = () => {
    if (loading) {
      return (
        <Badge variant="outline" className="bg-gray-100 text-gray-600 border-gray-200">
          <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
          Checking...
        </Badge>
      )
    }

    if (!status) return null

    if (status.shared_service_account) {
      return (
        <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
          <Shield className="w-3 h-3 mr-1" />
          Leadership Access Ready
        </Badge>
      )
    } else if (status.cached_data_available && status.cache_valid) {
      return (
        <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">
          <Clock className="w-3 h-3 mr-1" />
          Cached Data Available
        </Badge>
      )
    } else if (status.cached_data_available) {
      return (
        <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-200">
          <Clock className="w-3 h-3 mr-1" />
          Cached Data (Stale)
        </Badge>
      )
    } else {
      return (
        <Badge variant="outline" className="bg-gray-100 text-gray-600 border-gray-200">
          <Settings className="w-3 h-3 mr-1" />
          Individual Access Only
        </Badge>
      )
    }
  }

  if (!showDetails) {
    return (
      <div className="flex items-center gap-2">
        {getStatusBadge()}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowDetails(true)}
          className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
        >
          <Info className="w-3 h-3 mr-1" />
          Details
        </Button>
      </div>
    )
  }

  return (
    <Card className="w-80">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Crown className="w-4 h-4 text-purple-600" />
            Leadership Access Status
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDetails(false)}
            className="text-xs"
          >
            ✕
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Current Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Access Mode:</span>
          {getStatusBadge()}
        </div>

        {/* Status Details */}
        {status && (
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2">
              {status.shared_service_account ? (
                <CheckCircle className="w-3 h-3 text-green-600" />
              ) : (
                <AlertTriangle className="w-3 h-3 text-gray-400" />
              )}
              <span className={status.shared_service_account ? "text-green-800" : "text-gray-500"}>
                Shared Service Account
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              {status.cached_data_available ? (
                <CheckCircle className="w-3 h-3 text-blue-600" />
              ) : (
                <AlertTriangle className="w-3 h-3 text-gray-400" />
              )}
              <span className={status.cached_data_available ? "text-blue-800" : "text-gray-500"}>
                Cached Analytics Data
              </span>
            </div>

            {status.last_cache_update && (
              <div className="flex items-center gap-2 text-gray-500">
                <Clock className="w-3 h-3" />
                Last updated: {formatLastUpdate(status.last_cache_update)}
              </div>
            )}
          </div>
        )}

        {/* How It Works */}
        <Alert className="border-blue-200 bg-blue-50">
          <Info className="h-3 w-3" />
          <AlertDescription className="text-xs">
            <strong>How it works:</strong> If you don't have individual Jira access, the system automatically uses leadership access for executive insights.
          </AlertDescription>
        </Alert>

        {/* Action Button */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={checkLeadershipStatus}
            disabled={loading}
            className="text-xs"
          >
            {loading && <RefreshCw className="w-3 h-3 mr-1 animate-spin" />}
            Refresh
          </Button>
          
          {!status?.leadership_access_available && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                // Navigate to integration tab
                window.location.href = '/?tab=leadership'
              }}
              className="text-xs"
            >
              <Settings className="w-3 h-3 mr-1" />
              Setup
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
