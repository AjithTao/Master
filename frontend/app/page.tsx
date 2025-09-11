'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { Button } from './components/ui/button'
import { SimpleJiraConnect } from './components/SimpleJiraConnect'
import { SimpleConfluenceConnect } from './components/SimpleConfluenceConnect'
import { ApiStatusIndicator } from './components/ApiStatusIndicator'
import { ChatInterface } from './components/ChatInterface'
import { LeadershipInsights } from './components/LeadershipInsights'
import { DashboardPage } from './components/DashboardPage'
import { EnhancedLeadershipDashboard } from './components/EnhancedLeadershipDashboard'
import LeadershipStatusIndicator from './components/LeadershipStatusIndicator'
import { SimpleLeadershipConnect } from './components/SimpleLeadershipConnect'
import { BarChart3, MessageSquare, Settings, Crown, Database, FileText } from 'lucide-react'
import { useTheme } from './contexts/ThemeContext'
import { LoadingScreen } from './components/LoadingComponents'
import { ASSISTANT_NAME } from './constants'
import Link from 'next/link'

export default function Home() {
  const searchParams = useSearchParams()
  const [activeTab, setActiveTab] = useState('integration')
  const [integrationSelection, setIntegrationSelection] = useState<'jira' | 'confluence' | 'leadership'>('jira')
  
  // React to sidebar clicks by reading ?tab=jira|confluence|leadership
  useEffect(() => {
    const tabParam = (searchParams?.get('tab') || '').toLowerCase()
    if (tabParam === 'jira' || tabParam === 'confluence' || tabParam === 'leadership') {
      setIntegrationSelection(tabParam as 'jira' | 'confluence' | 'leadership')
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
      <div className="flex-shrink-0 bg-slate-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 transition-colors duration-200">
        {/* Welcome Section with Leadership Mode */}
        <div className="mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">Welcome back, Ajith</h2>
                <ApiStatusIndicator />
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Analyze your leadership patterns and team dynamics through Jira data with AI-powered insights
              </p>
            </div>
            <div className="flex-shrink-0 ml-6">
              <LeadershipStatusIndicator />
            </div>
          </div>
        </div>

         {/* Navigation Tabs */}
         <Tabs value={activeTab} onValueChange={setActiveTab}>
           <TabsList className="grid w-full grid-cols-4 bg-slate-100 dark:bg-gray-700 p-1 rounded-lg">
             <TabsTrigger 
               value="integration" 
               className="flex items-center gap-2 data-[state=active]:bg-slate-50 dark:data-[state=active]:bg-gray-600 data-[state=active]:shadow-sm transition-all duration-200"
             >
               <Settings className="w-4 h-4" />
               Integration
             </TabsTrigger>
             <TabsTrigger 
               value="chat" 
               className="flex items-center gap-2 data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:shadow-sm transition-all duration-200 relative overflow-hidden"
             >
               <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 via-purple-400/20 to-blue-400/20 animate-pulse"></div>
               <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer"></div>
               <div className="absolute inset-0 rounded-md shadow-lg shadow-blue-400/20 animate-glow"></div>
               <MessageSquare className="w-4 h-4 relative z-10" />
               <span className="relative z-10">{ASSISTANT_NAME}</span>
             </TabsTrigger>
             <TabsTrigger 
               value="insights" 
               className="flex items-center gap-2 data-[state=active]:bg-slate-50 dark:data-[state=active]:bg-gray-600 data-[state=active]:shadow-sm transition-all duration-200"
             >
               <BarChart3 className="w-4 h-4" />
               Leadership Insights
             </TabsTrigger>
             <TabsTrigger 
               value="dashboard" 
               className="flex items-center gap-2 data-[state=active]:bg-slate-50 dark:data-[state=active]:bg-gray-600 data-[state=active]:shadow-sm transition-all duration-200"
             >
               <BarChart3 className="w-4 h-4" />
               Dashboard
             </TabsTrigger>
           </TabsList>
         </Tabs>
      </div>

       {/* Main Content Area */}
       <div className="flex-1 min-h-0 p-6 bg-gradient-to-br from-slate-50 via-blue-50/40 to-indigo-50/30 dark:from-gray-900 dark:via-blue-900/10 dark:to-purple-900/10 transition-colors duration-200">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full min-h-0 flex-1">

        <TabsContent value="integration" className="space-y-6">
          {/* Integration Sub-Navigation */}
          <div className="flex flex-wrap gap-3 mb-6">
            <Button
              variant={integrationSelection === 'jira' ? 'default' : 'outline'}
              onClick={() => setIntegrationSelection('jira')}
              size="sm"
              className={`flex items-center gap-2 transition-all duration-200 ${
                integrationSelection === 'jira' 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg' 
                  : 'hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300'
              }`}
            >
              <Database className="w-4 h-4" />
              Jira
            </Button>
            <Button
              variant={integrationSelection === 'confluence' ? 'default' : 'outline'}
              onClick={() => setIntegrationSelection('confluence')}
              size="sm"
              className={`flex items-center gap-2 transition-all duration-200 ${
                integrationSelection === 'confluence' 
                  ? 'bg-green-600 hover:bg-green-700 text-white shadow-lg' 
                  : 'hover:bg-green-50 dark:hover:bg-green-900/20 hover:border-green-300'
              }`}
            >
              <FileText className="w-4 h-4" />
              Confluence
            </Button>
            <Button
              variant={integrationSelection === 'leadership' ? 'default' : 'outline'}
              onClick={() => setIntegrationSelection('leadership')}
              size="sm"
              className={`flex items-center gap-2 transition-all duration-200 ${
                integrationSelection === 'leadership' 
                  ? 'bg-purple-600 hover:bg-purple-700 text-white shadow-lg' 
                  : 'hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:border-purple-300'
              }`}
            >
              <Crown className="w-4 h-4" />
              Leadership Access
            </Button>
          </div>

          {/* Integration Content */}
          {integrationSelection === 'leadership' ? (
            <div className="max-w-6xl mx-auto">
              <SimpleLeadershipConnect />
            </div>
          ) : (
            <div className="max-w-5xl mx-auto">
              <div className="transform transition-all duration-300 ease-in-out hover:scale-[1.02]">
                {integrationSelection === 'jira' ? <SimpleJiraConnect /> : <SimpleConfluenceConnect />}
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="chat" className="h-full min-h-0 flex-1">
          <div className="h-full min-h-0 flex flex-col">
            <ChatInterface />
          </div>
        </TabsContent>

        <TabsContent value="insights" className="h-full min-h-0 flex-1">
          <div className="h-full min-h-0 flex flex-col">
            <LeadershipInsights />
          </div>
        </TabsContent>

        <TabsContent value="dashboard" className="h-full min-h-0 flex-1">
          <div className="h-full min-h-0 flex flex-col">
            <EnhancedLeadershipDashboard />
          </div>
        </TabsContent>

        
        </Tabs>
      </div>
    </div>
  )
}
