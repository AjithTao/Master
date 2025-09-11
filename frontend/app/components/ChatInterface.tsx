'use client'

import { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react'
import { Button } from './ui/button'
import { Card, CardContent } from './ui/card'
import { Input } from './ui/input'
import { ScrollArea } from './ui/scroll-area'
import { Send, Loader2, Download, FileText, Presentation, Crown, Shield, Clock } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { useChat, Message } from '../contexts/ChatContext'
import { Badge } from './ui/badge'


interface ChatResponse {
  response: string
  error?: string
  jql?: string
  data?: any[]
  intent?: string
  success?: boolean
  decision: string
  metadata?: {
    type: string
    decision: string
  }
  mode?: string
  export_data?: {
    filename: string
    data: string
  }
  data_source?: string
  last_updated?: string
}

export const ChatInterface = forwardRef<{ sendQuickMessage: (message: string) => void }, {}>((props, ref) => {
  const { messages, addMessage, clearMessages, isLoading, setIsLoading, chatInterfaceRef, lastIssueDetails, setLastIssueDetails, lastProjectKey, setLastProjectKey } = useChat()
  const [input, setInput] = useState('')
  const [exportFiles, setExportFiles] = useState<{pdf?: string, powerpoint?: string}>({})
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const ISSUE_KEY_RE = /\b([A-Z][A-Z0-9]+-\d+)\b/

  const augmentMessageWithLastIssue = (original: string): string => {
    // Only apply for short property-style follow-ups
    const trimmed = original.trim().toLowerCase()
    const isPropertyFollowUp = /^(assignee|reporter|status|priority|type|summary|description|who|owner|open\s+link|url)\b/.test(trimmed)
      || /(assignee|reporter)\s+(for|of)\s+(this\s+)?(ticket|issue|story)\b/.test(trimmed)
      || /reporter name|assignee name/.test(trimmed)
    if (!isPropertyFollowUp) return original
    if (ISSUE_KEY_RE.test(original)) return original
    if (lastIssueDetails?.key) {
      return `${original} for ${lastIssueDetails.key}`
    }
    return original
  }

  const augmentMessageWithLastProject = (original: string): string => {
    const trimmed = original.trim().toLowerCase()
    // Apply only for analytics/listing queries
    const isAnalyticsQuery = /(open|closed|in\s+progress|bugs|stories|tasks|issues|show|list|count)/.test(trimmed)
    if (!isAnalyticsQuery) return original
    // If any project key appears (simple heuristic of 2-5 uppercase letters), don't augment
    const projectKeyMatch = original.match(/\b([A-Z]{2,5})\b/)
    if (projectKeyMatch) return original
    if (lastProjectKey) {
      return `${original} in project ${lastProjectKey}`
    }
    return original
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessageDirectly = async (message: string) => {
    if (isLoading) return

    setIsLoading(true)

    // Add user message immediately
    addMessage({ role: 'user', content: message })

    try {
      let finalMessage = message
      
      // Always augment messages - the backend will handle leadership mode automatically
      finalMessage = augmentMessageWithLastIssue(message)
      finalMessage = augmentMessageWithLastProject(finalMessage)
      
      // Always use the main chat endpoint - it will automatically route to leadership mode if needed
      const endpoint = 'http://localhost:8000/api/chat'
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: finalMessage }),
      })

      const data: ChatResponse = await response.json()

      if (response.ok) {
        // Check if this was automatic leadership mode
        const isAutoLeadershipMode = (data as any).auto_leadership_mode || false
        const actualLeadershipMode = isAutoLeadershipMode
        
        // Add leadership mode metadata to assistant messages
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response || data.error || 'No response received',
          isLeadershipMode: actualLeadershipMode,
          dataSource: (data as any).data_source,
          lastUpdated: (data as any).last_updated
        }
        
        // Add helpful message if auto-leadership was used
        if (isAutoLeadershipMode && (data as any).message) {
          assistantMessage.content = `${(data as any).message}\n\n${data.response || data.error || 'No response received'}`
        }
        
        addMessage(assistantMessage)
        // If an issue key is present, fetch details for cache (only in regular mode)
        const responseText = typeof data.response === 'string' ? data.response : JSON.stringify(data.response)
        const match = !actualLeadershipMode && responseText && responseText.match(ISSUE_KEY_RE)
        if (match && match[1]) {
          const key = match[1]
          try {
            const dresp = await fetch(`http://localhost:8000/api/jira/issue/${key}`)
            const djson = await dresp.json()
            if (dresp.ok && djson.issue) {
              setLastIssueDetails({ key, data: djson.issue, fetchedAt: new Date().toISOString() })
              if (djson.issue?.project) {
                setLastProjectKey(djson.issue.project)
              }
            }
          } catch {}
        }
      } else {
        addMessage({ 
          role: 'assistant', 
          content: `Error: ${data.error || data.response || 'Failed to get response'}` 
        })
      }
      
      // Handle Excel export downloads
      if (data.mode === 'export' && data.export_data) {
        const { filename, data: excelData } = data.export_data
        const blob = new Blob([Uint8Array.from(atob(excelData), c => c.charCodeAt(0))], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      addMessage({ 
        role: 'assistant', 
        content: `Network error: ${error}` 
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useImperativeHandle(ref, () => ({
    sendQuickMessage: (message: string) => {
      sendMessageDirectly(message)
    }
  }))

  // Register this component with the context
  useEffect(() => {
    console.log('ChatInterface: Registering with context')
    // Assign through a local variable to satisfy readonly typing on refs
    const refObj = {
      sendQuickMessage: sendMessageDirectly
    } as { sendQuickMessage: (message: string) => void }
    // @ts-expect-error allow setting from provider since it's a mutable ref in context
    chatInterfaceRef.current = refObj
    console.log('ChatInterface: Registered successfully')
  }, [sendMessageDirectly])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message immediately
    addMessage({ role: 'user', content: userMessage })

    // If this is a quick property question and we have lastIssueDetails, answer locally
    try {
      const low = userMessage.toLowerCase()
      const isPropertyFollowUp = /^(assignee|reporter|status|priority|type|summary|description|url|link|open)$/i.test(userMessage.trim()) || /reporter name|assignee name/i.test(userMessage)
      const asksIssueDetails = /(details|info|summary).*\b(ccm|hcat|[A-Z]{2,5})-\d+/i.test(userMessage)
      const asksProjectDetails = /project (details|summary|info)/i.test(userMessage)

      if ((isPropertyFollowUp || asksIssueDetails) && lastIssueDetails) {
        const issue = lastIssueDetails.data
        let reply = `${lastIssueDetails.key}: ${issue?.summary || ''}\n` +
          `Status: ${issue?.status || 'Unknown'}  Type: ${issue?.type || 'Unknown'}  Priority: ${issue?.priority || 'Unknown'}\n` +
          `Assignee: ${issue?.assignee?.name || 'Unassigned'}  Reporter: ${issue?.reporter?.name || 'Unknown'}  Project: ${issue?.project || 'Unknown'}`
        if (/^assignee/i.test(userMessage)) reply = `Assignee: ${issue?.assignee?.name || 'Unassigned'}`
        if (/^reporter/i.test(userMessage) || /reporter name/i.test(userMessage)) {
          const reporterName = issue?.reporter?.name || 'Unknown'
          const reporterEmail = issue?.reporter?.email || ''
          const issueSummary = issue?.summary || 'this issue'
          reply = `${reporterName} is the reporter for ${lastIssueDetails.key}. ${reporterEmail ? `You can reach them at ${reporterEmail} for context or clarification about ${issueSummary}.` : `They initiated ${issueSummary}.`}`
        }
        if (/^status/i.test(userMessage)) reply = `Status: ${issue?.status || 'Unknown'}`
        if (/^priority/i.test(userMessage)) reply = `Priority: ${issue?.priority || 'Unknown'}`
        if (/^type/i.test(userMessage)) reply = `Type: ${issue?.type || 'Unknown'}`
        if (/^(url|link|open)/i.test(userMessage)) reply = issue?.url ? `Open: ${issue.url}` : 'No URL available'
        addMessage({ role: 'assistant', content: reply })
        setIsLoading(false)
        return
      }

      if (asksProjectDetails && lastProjectKey) {
        const proj = lastProjectKey
        addMessage({ role: 'assistant', content: `Project: ${proj}. Ask me to list open issues, open stories, bugs, or sprint analytics for this project.` })
        setIsLoading(false)
        return
      }
    } catch {}

    try {
      let finalMessage = augmentMessageWithLastIssue(userMessage)
      finalMessage = augmentMessageWithLastProject(finalMessage)
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: finalMessage }),
      })

      const data: ChatResponse = await response.json()

      if (response.ok) {
        // Check if this was automatic leadership mode
        const isAutoLeadershipMode = (data as any).auto_leadership_mode || false
        const actualLeadershipMode = isAutoLeadershipMode
        
        // Add leadership mode metadata to assistant messages
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response || data.error || 'No response received',
          isLeadershipMode: actualLeadershipMode,
          dataSource: (data as any).data_source,
          lastUpdated: (data as any).last_updated
        }
        
        // Add helpful message if auto-leadership was used
        if (isAutoLeadershipMode && (data as any).message) {
          assistantMessage.content = `${(data as any).message}\n\n${data.response || data.error || 'No response received'}`
        }
        
        addMessage(assistantMessage)
        // If an issue key is present, fetch details for cache (only in regular mode)
        const responseText = typeof data.response === 'string' ? data.response : JSON.stringify(data.response)
        const match = !actualLeadershipMode && responseText && responseText.match(ISSUE_KEY_RE)
        if (match && match[1]) {
          const key = match[1]
          try {
            const dresp = await fetch(`http://localhost:8000/api/jira/issue/${key}`)
            const djson = await dresp.json()
            if (dresp.ok && djson.issue) {
              setLastIssueDetails({ key, data: djson.issue, fetchedAt: new Date().toISOString() })
              if (djson.issue?.project) {
                setLastProjectKey(djson.issue.project)
              }
            }
          } catch {}
        }
      } else {
        addMessage({ 
          role: 'assistant', 
          content: `Error: ${data.error || data.response || 'Failed to get response'}` 
        })
      }
      
      // Handle Excel export downloads
      if (data.mode === 'export' && data.export_data) {
        const { filename, data: excelData } = data.export_data
        const blob = new Blob([Uint8Array.from(atob(excelData), c => c.charCodeAt(0))], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      addMessage({ 
        role: 'assistant', 
        content: `Network error: ${error}` 
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const exportToPDF = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/export/pdf', {
        method: 'POST'
      })
      const data = await response.json()
      
      if (response.ok) {
        setExportFiles(prev => ({ ...prev, pdf: data.file_path }))
        // Trigger download
        window.open(`http://localhost:8000/api/export/download/pdf`, '_blank')
      } else {
        alert('PDF export failed: ' + data.detail)
      }
    } catch (error) {
      alert('PDF export failed: ' + error)
    }
  }

  const exportToPowerPoint = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/export/powerpoint', {
        method: 'POST'
      })
      const data = await response.json()
      
      if (response.ok) {
        setExportFiles(prev => ({ ...prev, powerpoint: data.file_path }))
        // Trigger download
        window.open(`http://localhost:8000/api/export/download/powerpoint`, '_blank')
      } else {
        alert('PowerPoint export failed: ' + data.detail)
      }
    } catch (error) {
      alert('PowerPoint export failed: ' + error)
    }
  }

  const exportToExcel = async () => {
    try {
      // Trigger server-side Excel generation using last JQL context
      const resp = await fetch('http://localhost:8000/api/jira/export/excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      })
      const data = await resp.json()
      if (resp.ok && data?.data && data?.filename) {
        const blob = new Blob([Uint8Array.from(atob(data.data), c => c.charCodeAt(0))], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = data.filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      } else {
        alert(data?.detail || data?.message || 'Excel export failed')
      }
    } catch (e) {
      alert('Excel export failed: ' + e)
    }
  }

  const clearChat = async () => {
    try {
      await fetch('http://localhost:8000/api/chat/clear', {
        method: 'POST'
      })
      clearMessages()
    } catch (error) {
      console.error('Failed to clear chat:', error)
    }
  }

  return (
    <Card className="h-full min-h-0 flex flex-col overflow-hidden">
      <CardContent className="p-0 h-full min-h-0 flex flex-col overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 min-h-0">
        <ScrollArea className="h-full p-6">
          <div className="space-y-4">
            {/* Last viewed issue panel intentionally hidden per request */}
            {messages.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gray-100 dark:bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                  <Send className="w-8 h-8 text-gray-400 dark:text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Start a Conversation</h3>
                <p className="text-gray-600 dark:text-muted-foreground">
                  Ask me anything about your Jira data, documents, or get general assistance
                </p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white dark:bg-primary dark:text-primary-foreground'
                        : message.isLeadershipMode 
                        ? 'bg-purple-50 text-gray-900 dark:bg-purple-900/20 dark:text-foreground border border-purple-200'
                        : 'bg-gray-100 text-gray-900 dark:bg-muted dark:text-foreground'
                    }`}
                  >
                    {/* Leadership Mode Indicator */}
                    {message.role === 'assistant' && message.isLeadershipMode && (
                      <div className="flex items-center gap-2 mb-2 text-xs">
                        <Badge variant="secondary" className="bg-purple-100 text-purple-800 border-purple-200">
                          <Crown className="w-3 h-3 mr-1" />
                          Leadership Mode
                        </Badge>
                        {message.dataSource === 'live_jira_data' ? (
                          <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
                            <Shield className="w-3 h-3 mr-1" />
                            Live Data
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-200">
                            <Clock className="w-3 h-3 mr-1" />
                            Cached Data
                          </Badge>
                        )}
                        {message.lastUpdated && (
                          <span className="text-gray-500">
                            Updated {new Date(message.lastUpdated).toLocaleTimeString()}
                          </span>
                        )}
                      </div>
                    )}
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                          em: ({ children }) => <em className="italic">{children}</em>,
                          code: ({ children }) => (
                            <code className="bg-gray-200 text-gray-900 dark:bg-accent dark:text-accent-foreground px-1 py-0.5 rounded text-sm font-mono">
                              {children}
                            </code>
                          ),
                          pre: ({ children }) => (
                            <pre className="bg-gray-200 text-gray-900 dark:bg-accent dark:text-accent-foreground p-3 rounded overflow-x-auto text-sm">
                              {children}
                            </pre>
                          ),
                          ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                          li: ({ children }) => <li className="mb-1">{children}</li>,
                        }}
                      >
                        {typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-muted rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-gray-600 dark:text-muted-foreground">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
        </div>

        {/* Export Options */}
        {messages.length > 0 && (
          <div className="border-t border-gray-200 dark:border-border p-4 bg-gray-50 dark:bg-card">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-sm">Export Options</h4>
              <Button variant="ghost" size="sm" onClick={clearChat}>
                Clear Chat
              </Button>
            </div>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={exportToPDF}
                className="flex items-center space-x-2"
              >
                <FileText className="w-4 h-4" />
                <span>PDF</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={exportToExcel}
                className="flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Excel (full list)</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={exportToPowerPoint}
                className="flex items-center space-x-2"
              >
                <Presentation className="w-4 h-4" />
                <span>PowerPoint</span>
              </Button>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-border p-4 bg-white dark:bg-background">
          <div className="flex space-x-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your data, documents, or integrations..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              size="sm"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
})
