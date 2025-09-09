'use client'

import { useChat } from '../contexts/ChatContext'

export function RightSidebar() {
  const { chatInterfaceRef } = useChat()

  const handleQuickInsight = (message: string) => {
    console.log('RightSidebar: handleQuickInsight called with:', message)
    console.log('RightSidebar: chatInterfaceRef.current:', chatInterfaceRef.current)
    
    if (chatInterfaceRef.current) {
      console.log('RightSidebar: Calling sendQuickMessage')
      chatInterfaceRef.current.sendQuickMessage(message)
    } else {
      console.log('RightSidebar: chatInterfaceRef.current is null')
    }
  }

  return (
    <div className="space-y-6">
      <h3 className="font-semibold text-foreground">Quick Jira Insights</h3>
      <div className="space-y-3">
        <button 
          className="w-full p-3 text-left bg-card hover:bg-accent rounded-lg transition-colors border border-border"
          onClick={() => handleQuickInsight("Analyze Sprint 23 - Review velocity & burndown trends")}
        >
          <p className="font-medium text-foreground">Analyze Sprint 23</p>
          <p className="text-sm text-muted-foreground">Review velocity & burndown trends</p>
        </button>
        <button 
          className="w-full p-3 text-left bg-card hover:bg-accent rounded-lg transition-colors border border-border"
          onClick={() => handleQuickInsight("Team Workload Balance - Check current story point distribution")}
        >
          <p className="font-medium text-foreground">Team Workload Balance</p>
          <p className="text-sm text-muted-foreground">Check current story point distribution</p>
        </button>
        <button 
          className="w-full p-3 text-left bg-card hover:bg-accent rounded-lg transition-colors border border-border"
          onClick={() => handleQuickInsight("Leadership Impact - How decisions affect delivery")}
        >
          <p className="font-medium text-foreground">Leadership Impact</p>
          <p className="text-sm text-muted-foreground">How decisions affect delivery</p>
        </button>
        <button 
          className="w-full p-3 text-left bg-card hover:bg-accent rounded-lg transition-colors border border-border"
          onClick={() => handleQuickInsight("Identify Blockers - Find recurring impediments")}
        >
          <p className="font-medium text-foreground">Identify Blockers</p>
          <p className="text-sm text-muted-foreground">Find recurring impediments</p>
        </button>
      </div>
    </div>
  )
}
