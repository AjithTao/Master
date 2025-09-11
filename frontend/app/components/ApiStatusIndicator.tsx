'use client'

import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { getApiUrl } from '../../lib/api-config'

interface ApiStatusIndicatorProps {
  className?: string
}

export function ApiStatusIndicator({ className = '' }: ApiStatusIndicatorProps) {
  const [status, setStatus] = useState<'online' | 'offline' | 'error'>('offline')

  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await fetch(getApiUrl('/api/jira/status'))
        if (response.ok) {
          setStatus('online')
        } else {
          setStatus('error')
        }
      } catch (error) {
        setStatus('offline')
      }
    }

    checkApiStatus()
    // Check every 30 seconds
    const interval = setInterval(checkApiStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = () => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-3 h-3 text-green-500" />
      case 'offline':
        return <XCircle className="w-3 h-3 text-red-500" />
      case 'error':
        return <AlertCircle className="w-3 h-3 text-yellow-500" />
      default:
        return <XCircle className="w-3 h-3 text-gray-500" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'online':
        return 'Online'
      case 'offline':
        return 'Offline'
      case 'error':
        return 'Error'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 ${className}`}>
      <div className={`w-2 h-2 rounded-full animate-pulse ${
        status === 'online' ? 'bg-green-500' : 
        status === 'offline' ? 'bg-red-500' : 
        'bg-yellow-500'
      }`}></div>
      <span className={`${
        status === 'online' ? 'text-green-700 dark:text-green-400' : 
        status === 'offline' ? 'text-red-700 dark:text-red-400' : 
        'text-yellow-700 dark:text-yellow-400'
      }`}>
        {getStatusText()}
      </span>
    </div>
  )
}
