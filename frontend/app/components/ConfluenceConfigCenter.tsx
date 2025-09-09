'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'

export function ConfluenceConfigCenter() {
  const [url, setUrl] = useState('https://taodigital.atlassian.net/wiki')
  const [email, setEmail] = useState('')
  const [apiToken, setApiToken] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [currentEmail, setCurrentEmail] = useState('')

  const handleConfigure = async () => {
    setIsSaving(true)
    setMessage(null)
    setError(null)
    try {
      const resp = await fetch('http://localhost:8000/api/confluence/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, email, api_token: apiToken })
      })
      const data = await resp.json()
      if (resp.ok && data.success) {
        setMessage('Confluence configured successfully.')
        setIsConnected(true)
        setCurrentEmail(email)
        try {
          window.dispatchEvent(new CustomEvent('integration-update', { detail: { service: 'confluence', configured: true } }))
        } catch {}
      } else {
        setError(data.detail || 'Failed to configure Confluence')
      }
    } catch (e: any) {
      setError(e?.message || 'Network error')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDisconnect = async () => {
    setIsSaving(true)
    setMessage(null)
    setError(null)
    try {
      const resp = await fetch('http://localhost:8000/api/confluence/disconnect', { method: 'POST' })
      const data = await resp.json()
      if (resp.ok && data.success) {
        setIsConnected(false)
        setCurrentEmail('')
        setMessage('Confluence disconnected successfully.')
        try {
          window.dispatchEvent(new CustomEvent('integration-update', { detail: { service: 'confluence', configured: false } }))
        } catch {}
      } else {
        setError(data.detail || 'Failed to disconnect Confluence')
      }
    } catch (e: any) {
      setError(e?.message || 'Network error')
    } finally {
      setIsSaving(false)
    }
  }

  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetch('http://localhost:8000/api/confluence/status')
        const data = await resp.json()
        if (resp.ok && data.configured) {
          setIsConnected(true)
          setUrl(data.config?.url || url)
          setCurrentEmail(data.config?.email || '')
        } else {
          setIsConnected(false)
        }
      } catch {}
    }
    load()
  }, [])

  return (
    <Card className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
      <CardHeader>
        <CardTitle>Confluence Integration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isConnected ? (
          <div className="text-center py-6">
            <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-green-700 dark:text-green-300 text-2xl">✓</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Confluence Connected</h3>
            <p className="text-gray-600 dark:text-muted-foreground mb-4">Connected to {url}</p>
            <p className="text-sm text-gray-600 dark:text-muted-foreground mb-6">Email: {currentEmail || email}</p>
            <div className="flex">
              <Button onClick={handleDisconnect} variant="outline" className="w-full" disabled={isSaving}>
                {isSaving ? 'Disconnecting…' : 'Disconnect'}
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div>
              <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">Confluence URL</label>
              <input
                className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 p-2 text-sm"
                placeholder="https://<site>.atlassian.net/wiki"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">Email</label>
                <input
                  className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 p-2 text-sm"
                  placeholder="your.email@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">API Token</label>
                <input
                  className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 p-2 text-sm"
                  placeholder="Atlassian API token"
                  value={apiToken}
                  onChange={(e) => setApiToken(e.target.value)}
                  type="password"
                />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button onClick={handleConfigure} disabled={isSaving}>
                {isSaving ? 'Configuring…' : 'Configure Confluence'}
              </Button>
              {message && <span className="text-sm text-green-600 dark:text-green-400">{message}</span>}
              {error && <span className="text-sm text-red-600 dark:text-red-400">{error}</span>}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Generate an API token at id.atlassian.com → Security → API tokens and use your Atlassian email.
            </p>
          </>
        )}
      </CardContent>
    </Card>
  )
}


