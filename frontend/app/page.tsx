'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { JiraConfigCenter } from './components/JiraConfigCenter'
import { ConfluenceConfigCenter } from './components/ConfluenceConfigCenter'
import { StatusIndicators } from './components/StatusIndicators'
import { ChatInterface } from './components/ChatInterface'
import { LeadershipInsights } from './components/LeadershipInsights'
import { DashboardPage } from './components/DashboardPage'
import { BarChart3, MessageSquare, Settings } from 'lucide-react'
import { useTheme } from './contexts/ThemeContext'
import { LoadingScreen } from './components/LoadingComponents'
import { ASSISTANT_NAME } from './constants'
import Link from 'next/link'

export default function Home() {
  const searchParams = useSearchParams()
  const [activeTab, setActiveTab] = useState('integration')
  const [integrationSelection, setIntegrationSelection] = useState<'jira' | 'confluence'>('jira')
  
  // React to sidebar clicks by reading ?tab=jira|confluence
  useEffect(() => {
    const tabParam = (searchParams?.get('tab') || '').toLowerCase()
    if (tabParam === 'jira' || tabParam === 'confluence') {
      setIntegrationSelection(tabParam)
      setActiveTab('integration')
    }
  }, [searchParams])
  const { isLoading } = useTheme()

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <div className="h-screen min-h-screen flex flex-col">
      {/* Fixed Top Navigation */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 transition-colors duration-200">
        {/* Welcome Section */}
        <div className="mb-6">
          <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">Welcome back, Ajith</h2>
          <p className="text-gray-600 dark:text-gray-300">
            Analyze your leadership patterns and team dynamics through Jira data with AI-powered insights
          </p>
        </div>

        {/* Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 bg-gray-100 dark:bg-gray-700">
            <TabsTrigger value="integration" className="flex items-center gap-2 data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600">
              <Settings className="w-4 h-4" />
              Integration
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2 data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 via-purple-400/20 to-blue-400/20 animate-pulse"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer"></div>
              <div className="absolute inset-0 rounded-md shadow-lg shadow-blue-400/20 animate-glow"></div>
              <MessageSquare className="w-4 h-4 relative z-10" />
              <span className="relative z-10">{ASSISTANT_NAME}</span>
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center gap-2 data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600">
              <BarChart3 className="w-4 h-4" />
              Leadership Insights
            </TabsTrigger>
            <TabsTrigger value="dashboard" className="flex items-center gap-2 data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600">
              <BarChart3 className="w-4 h-4" />
              Dashboard
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Main Content Area (chat stays fixed; inner components manage their own scroll) */}
      <div className="flex-1 min-h-0 overflow-hidden p-6 bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full min-h-0 flex-1 overflow-hidden">

        <TabsContent value="integration" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-full">
              {integrationSelection === 'jira' ? <JiraConfigCenter /> : <ConfluenceConfigCenter />}
            </div>
            <div className="h-full">
              <StatusIndicators />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="chat" className="h-full min-h-0 flex-1 overflow-hidden">
          <div className="h-full min-h-0 flex flex-col overflow-hidden">
            <ChatInterface />
          </div>
        </TabsContent>

        <TabsContent value="insights" className="h-full min-h-0 flex-1 overflow-hidden">
          <div className="h-full min-h-0 flex flex-col overflow-hidden">
            <LeadershipInsights />
          </div>
        </TabsContent>

        <TabsContent value="dashboard" className="space-y-6">
          <div className="w-full">
            {/* Simple placeholder that we will flesh out in DashboardPage */}
            <DashboardPage />
          </div>
        </TabsContent>

        
        </Tabs>
      </div>
    </div>
  )
}
