'use client'

import { createContext, useContext, useState, useEffect, ReactNode, useRef } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  metadata?: any
}

interface CachedIssueDetails {
  key: string
  data: any
  fetchedAt: string
}

interface ChatContextType {
  messages: Message[]
  addMessage: (message: Message) => void
  clearMessages: () => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
  chatInterfaceRef: React.RefObject<{ sendQuickMessage: (message: string) => void }>
  lastIssueDetails: CachedIssueDetails | null
  setLastIssueDetails: (details: CachedIssueDetails | null) => void
  lastProjectKey: string | null
  setLastProjectKey: (project: string | null) => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)
  const chatInterfaceRef = useRef<{ sendQuickMessage: (message: string) => void }>(null)
  const [lastIssueDetails, setLastIssueDetails] = useState<CachedIssueDetails | null>(null)
  const [lastProjectKey, setLastProjectKey] = useState<string | null>(null)

  // Load messages from localStorage on mount
  useEffect(() => {
    console.log('ChatProvider: Initializing...')
    const savedMessages = localStorage.getItem('chat-messages')
    console.log('ChatProvider: Saved messages from localStorage:', savedMessages)
    const savedIssue = localStorage.getItem('chat-last-issue')
    const savedProject = localStorage.getItem('chat-last-project')
    
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages)
        setMessages(parsedMessages)
        console.log('ChatProvider: Loaded messages from localStorage:', parsedMessages.length)
      } catch (error) {
        console.error('ChatProvider: Failed to parse saved messages:', error)
      }
    } else {
      console.log('ChatProvider: No saved messages found')
    }
    if (savedIssue) {
      try {
        const parsedIssue = JSON.parse(savedIssue)
        setLastIssueDetails(parsedIssue)
      } catch (error) {
        console.error('ChatProvider: Failed to parse saved issue:', error)
      }
    }
    if (savedProject) {
      setLastProjectKey(savedProject)
    }
    setIsInitialized(true)
    console.log('ChatProvider: Initialization complete')
  }, [])

  // Save messages to localStorage whenever messages change (but not on initial load)
  useEffect(() => {
    if (isInitialized) {
      localStorage.setItem('chat-messages', JSON.stringify(messages))
      console.log('Saved messages to localStorage:', messages.length)
    }
  }, [messages, isInitialized])

  // Persist last issue cache
  useEffect(() => {
    if (isInitialized) {
      if (lastIssueDetails) {
        localStorage.setItem('chat-last-issue', JSON.stringify(lastIssueDetails))
      } else {
        localStorage.removeItem('chat-last-issue')
      }
    }
  }, [lastIssueDetails, isInitialized])

  // Persist last project key
  useEffect(() => {
    if (isInitialized) {
      if (lastProjectKey) {
        localStorage.setItem('chat-last-project', lastProjectKey)
      } else {
        localStorage.removeItem('chat-last-project')
      }
    }
  }, [lastProjectKey, isInitialized])

  const addMessage = (message: Message) => {
    const messageWithTimestamp = {
      ...message,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, messageWithTimestamp])
    console.log('ChatProvider: Added message:', messageWithTimestamp)
  }

  const clearMessages = () => {
    setMessages([])
    localStorage.removeItem('chat-messages')
    // Also clear last-issue cache when chat is cleared
    setLastIssueDetails(null)
    setLastProjectKey(null)
    localStorage.removeItem('chat-last-issue')
    localStorage.removeItem('chat-last-project')
    console.log('Cleared messages from localStorage')
  }

  return (
    <ChatContext.Provider value={{
      messages,
      addMessage,
      clearMessages,
      isLoading,
      setIsLoading,
      chatInterfaceRef,
      lastIssueDetails,
      setLastIssueDetails,
      lastProjectKey,
      setLastProjectKey
    }}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}
