'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Alert, AlertDescription } from './ui/alert'
import { 
  BarChart3, 
  Download, 
  TrendingUp, 
  Users, 
  FolderOpen, 
  Bug, 
  CheckSquare, 
  Loader2,
  RefreshCw,
  AlertCircle,
  Activity,
  Target,
  Zap,
  Calendar,
  Info,
  Sparkles,
  Clock,
  TrendingDown,
  Award,
  AlertTriangle
} from 'lucide-react'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

interface JiraAnalytics {
  summary: {
    total_projects: number
    total_stories: number
    total_defects: number
    total_tasks: number
    total_issues: number
    total_assignees: number
  }
  projects: Record<string, {
    name: string
    stories: number
    defects: number
    tasks: number
    total_issues: number
    assignee_count: number
    assignees: string[]
  }>
  current_sprint?: {
    name: string
    state: string
    startDate?: string
    endDate?: string
  }
  generated_at: string
}

interface StrategicInsights {
  ai_analysis: string
  risk_assessment: Array<{
    type: 'high' | 'medium' | 'low'
    description: string
    impact: string
    recommendation: string
  }>
  opportunities: Array<{
    title: string
    description: string
    potential_impact: string
  }>
  key_recommendations: Array<{
    priority: 'urgent' | 'high' | 'medium'
    action: string
    expected_outcome: string
    timeline: string
  }>
}

export function LeadershipInsights() {
  const [analytics, setAnalytics] = useState<JiraAnalytics | null>(null)
  const [strategicInsights, setStrategicInsights] = useState<StrategicInsights | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState('')
  const [selectedProject, setSelectedProject] = useState<string>('ALL')
  const [availableProjects, setAvailableProjects] = useState<any[]>([])
  const [includeAI, setIncludeAI] = useState(true)
  const printRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchProjects()
    fetchAnalytics()
  }, [])

  useEffect(() => {
    fetchAnalytics()
  }, [selectedProject, includeAI])

  const fetchProjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jira/projects')
      const data = await response.json()
      if (data.success && data.projects?.detailed) {
        setAvailableProjects(data.projects.detailed)
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    }
  }

  const fetchAnalytics = async () => {
    setIsLoading(true)
    setError('')
    
    try {
      const baseUrl = selectedProject === 'ALL' 
        ? 'http://localhost:8000/api/jira/analytics'
        : `http://localhost:8000/api/jira/analytics?project=${selectedProject}`
      
      const url = includeAI ? `${baseUrl}${selectedProject === 'ALL' ? '?' : '&'}include_strategic_ai=true` : baseUrl
      
      const response = await fetch(url)
      const data = await response.json()
      
      if (response.ok && data.success) {
        setAnalytics(data.analytics)
        if (data.strategic_insights) {
          setStrategicInsights(data.strategic_insights)
        } else {
          setStrategicInsights(null)
        }
      } else {
        setError(data.detail || 'Failed to fetch analytics')
      }
    } catch (error) {
      setError('Network error: ' + error)
    } finally {
      setIsLoading(false)
    }
  }

  const exportAnalytics = async (format: 'json' | 'csv') => {
    setIsExporting(true)
    
    try {
      const response = await fetch('http://localhost:8000/api/jira/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ format }),
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        // Create download link
        const blob = new Blob([format === 'json' ? JSON.stringify(data.data, null, 2) : data.data], {
          type: format === 'json' ? 'application/json' : 'text/csv'
        })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = data.filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        setError(data.detail || 'Export failed')
      }
    } catch (error) {
      setError('Export error: ' + error)
    } finally {
      setIsExporting(false)
    }
  }

  const exportPDF = async () => {
    if (!printRef.current) return
    
    setIsExporting(true)
    try {
      const element = printRef.current
      
      // Temporarily adjust styles for better PDF rendering
      const originalWidth = element.style.width
      const originalBg = element.style.backgroundColor
      element.style.width = '1200px'
      element.style.backgroundColor = '#ffffff'
      
      // Force dark mode elements to light for PDF
      const darkElements = element.querySelectorAll('.dark\\:bg-gray-800, .dark\\:bg-gray-900, .dark\\:text-white')
      const originalStyles = Array.from(darkElements).map(el => {
        const original = (el as HTMLElement).style.cssText
        ;(el as HTMLElement).style.backgroundColor = '#ffffff'
        ;(el as HTMLElement).style.color = '#000000'
        return original
      })
      
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        width: 1200,
        height: element.scrollHeight,
        scrollX: 0,
        scrollY: 0,
        windowWidth: 1200,
        windowHeight: element.scrollHeight,
        allowTaint: true,
        foreignObjectRendering: true
      })
      
      const imgData = canvas.toDataURL('image/png', 0.95)
      const pdf = new jsPDF('p', 'mm', 'a4')
      
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = pdf.internal.pageSize.getHeight()
      const imgWidth = pdfWidth - 20 // 10mm margin on each side
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      
      let heightLeft = imgHeight
      let position = 10 // 10mm top margin
      
      // Add title page
      pdf.setFontSize(24)
      pdf.setTextColor(0, 0, 0)
      pdf.text('Leadership Analytics Report', pdfWidth / 2, 30, { align: 'center' })
      pdf.setFontSize(12)
      pdf.text(`Generated: ${new Date().toLocaleString()}`, pdfWidth / 2, 40, { align: 'center' })
      pdf.text(`Project Filter: ${selectedProject}`, pdfWidth / 2, 50, { align: 'center' })
      
      // Add first page of content
      const firstPageHeight = Math.min(imgHeight, pdfHeight - 70)
      pdf.addImage(imgData, 'PNG', 10, 60, imgWidth, firstPageHeight, undefined, 'FAST')
      heightLeft -= firstPageHeight
      
      // Add additional pages if needed
      while (heightLeft > 0) {
        pdf.addPage()
        const pageHeight = Math.min(heightLeft, pdfHeight - 20)
        const sourceY = imgHeight - heightLeft
        
        // Create a new canvas for this page section
        const pageCanvas = document.createElement('canvas')
        const pageCtx = pageCanvas.getContext('2d')
        pageCanvas.width = canvas.width
        pageCanvas.height = (pageHeight / imgWidth) * canvas.width
        
        if (pageCtx) {
          pageCtx.drawImage(canvas, 0, (sourceY / imgWidth) * canvas.width, canvas.width, pageCanvas.height, 0, 0, canvas.width, pageCanvas.height)
          const pageImgData = pageCanvas.toDataURL('image/png', 0.95)
          pdf.addImage(pageImgData, 'PNG', 10, 10, imgWidth, pageHeight, undefined, 'FAST')
        }
        
        heightLeft -= pageHeight
      }
      
      pdf.save(`leadership-analytics-${selectedProject}-${new Date().toISOString().split('T')[0]}.pdf`)
      
      // Restore original styles
      element.style.width = originalWidth
      element.style.backgroundColor = originalBg
      darkElements.forEach((el, index) => {
        ;(el as HTMLElement).style.cssText = originalStyles[index]
      })
      
    } catch (error) {
      console.error('PDF export failed:', error)
      setError('PDF export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  const getRiskColor = (type: string) => {
    switch (type) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'outline'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'destructive'
      case 'high': return 'default'
      case 'medium': return 'secondary'
      default: return 'outline'
    }
  }

  if (isLoading && !analytics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading Jira analytics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!analytics) {
    return (
      <div className="text-center py-8">
        <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">No Analytics Available</h3>
        <p className="text-gray-600">Connect to Jira to view leadership insights and analytics.</p>
      </div>
    )
  }

  // Mock data for impressive charts
  const velocityData = [
    { sprint: 'Sprint 20', completed: 45, planned: 50 },
    { sprint: 'Sprint 21', completed: 52, planned: 48 },
    { sprint: 'Sprint 22', completed: 38, planned: 45 },
    { sprint: 'Sprint 23', completed: 48, planned: 50 },
    { sprint: 'Sprint 24', completed: 55, planned: 52 },
    { sprint: 'Sprint 25', completed: 42, planned: 48 }
  ]

  const teamPerformance = [
    { name: 'Ashwin Thyagarajan', stories: 12, defects: 2, velocity: 8.5 },
    { name: 'Ashwini Kumar', stories: 8, defects: 1, velocity: 7.2 },
    { name: 'John Doe', stories: 15, defects: 3, velocity: 9.1 },
    { name: 'Jane Smith', stories: 10, defects: 1, velocity: 8.8 },
    { name: 'Mike Johnson', stories: 6, defects: 0, velocity: 6.5 }
  ]

  const projectDistribution = Object.entries(analytics.projects).map(([key, project]) => ({
    name: key,
    stories: project.stories,
    defects: project.defects,
    tasks: project.tasks
  }))

  // Simple AI analysis on velocity trend
  const velocityDeltas = velocityData.slice(1).map((v, i) => v.completed - velocityData[i].completed)
  const averageVelocityDelta = velocityDeltas.reduce((a, b) => a + b, 0) / (velocityDeltas.length || 1)
  const lastCompleted = velocityData[velocityData.length - 1]?.completed || 0
  const projectedNextVelocity = Math.max(0, Math.round(lastCompleted + averageVelocityDelta))
  const velocityTrend = averageVelocityDelta > 0 ? 'upward' : averageVelocityDelta < 0 ? 'downward' : 'flat'
  const defectRatio = analytics.summary.total_stories > 0 
    ? (analytics.summary.total_defects / analytics.summary.total_stories) * 100 
    : 0

  return (
    <div className="h-full min-h-0 flex flex-col overflow-hidden" ref={printRef}>
      <div className="flex-shrink-0">
        {/* Header with Export Options */}
        <div className="flex flex-col space-y-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Leadership Analytics Dashboard
              </h2>
              <p className="text-gray-600 dark:text-muted-foreground mt-1">
                Real-time insights, velocity tracking, and team performance analytics
              </p>
            </div>
            <div className="flex space-x-2">
              <Button onClick={exportPDF} disabled={isExporting} className="flex items-center space-x-2 bg-blue-600 text-white hover:bg-blue-700">
                <Download className="w-4 h-4" />
                <span>PDF</span>
              </Button>
              <Button variant="outline" onClick={() => exportAnalytics('json')} disabled={isExporting} className="flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export</span>
              </Button>
              <Button variant="outline" onClick={fetchAnalytics} disabled={isLoading} className="flex items-center space-x-2">
                <RefreshCw className={`${isLoading ? 'animate-spin' : ''} w-4 h-4`} />
                <span>Refresh</span>
              </Button>
            </div>
          </div>
          
          {/* Project Filter */}
          <div className="flex flex-col space-y-2">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Project Filter:</h3>
            <div className="flex flex-wrap gap-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="project-insights"
                  value="ALL"
                  checked={selectedProject === 'ALL'}
                  onChange={(e) => setSelectedProject(e.target.value)}
                  className="text-blue-600"
                />
                <Badge variant={selectedProject === 'ALL' ? 'default' : 'outline'}>All Projects</Badge>
              </label>
              {availableProjects.map((proj) => (
                <label key={proj.key} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="project-insights"
                    value={proj.key}
                    checked={selectedProject === proj.key}
                    onChange={(e) => setSelectedProject(e.target.value)}
                    className="text-blue-600"
                  />
                  <Badge variant={selectedProject === proj.key ? 'default' : 'outline'}>
                    {proj.key} - {proj.name}
                  </Badge>
                </label>
              ))}
            </div>
            <p className="text-xs text-gray-500">
              {selectedProject === 'ALL' ? 'Showing analytics for all projects' : `Showing analytics for ${selectedProject}`}
            </p>
          </div>
          
          {/* AI Analysis Toggle */}
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <div className="flex items-center space-x-3">
              <Sparkles className="w-5 h-5 text-indigo-600 animate-pulse" />
              <div>
                <h4 className="font-semibold text-indigo-900 dark:text-indigo-100">AI-Powered Strategic Analysis</h4>
                <p className="text-sm text-indigo-700 dark:text-indigo-300">Get OpenAI-powered insights, risk assessment, and recommendations</p>
              </div>
            </div>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={includeAI}
                onChange={(e) => setIncludeAI(e.target.checked)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm font-medium text-indigo-900 dark:text-indigo-100">Enable AI Analysis</span>
            </label>
          </div>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 min-h-0 overflow-y-auto space-y-6">
        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className={`bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800 transition-all duration-500 hover:shadow-lg hover:scale-105 ${isLoading ? 'animate-pulse' : 'animate-in slide-in-from-left-4'}`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-sm font-medium text-blue-600 dark:text-blue-300">Total Projects</p>
                    <div className="group relative">
                      <Info className="h-3 w-3 text-blue-400 cursor-help" />
                      <div className="absolute left-0 top-5 hidden group-hover:block bg-black text-white text-xs rounded p-2 w-48 z-10">
                        Active projects with at least 1 issue in the selected timeframe
                      </div>
                    </div>
                  </div>
                  {isLoading ? (
                    <div className="h-9 bg-blue-200 rounded animate-pulse mb-1"></div>
                  ) : (
                    <p className="text-3xl font-bold text-blue-700 dark:text-blue-200 animate-in fade-in-50 duration-1000">
                      {analytics.summary.total_projects}
                    </p>
                  )}
                  <p className="text-xs text-blue-500 mt-1 animate-in slide-in-from-bottom-2 duration-700 delay-200">
                    {selectedProject === 'ALL' ? 'All Projects' : `${selectedProject} Project`}
                  </p>
                </div>
                <div className="p-3 bg-blue-500 rounded-full animate-in scale-in-75 duration-500 delay-300">
                  <FolderOpen className="w-6 h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className={`bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800 transition-all duration-500 hover:shadow-lg hover:scale-105 ${isLoading ? 'animate-pulse' : 'animate-in slide-in-from-left-4 delay-150'}`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-sm font-medium text-green-600 dark:text-green-300">Total Stories</p>
                    <div className="group relative">
                      <Info className="h-3 w-3 text-green-400 cursor-help" />
                      <div className="absolute left-0 top-5 hidden group-hover:block bg-black text-white text-xs rounded p-2 w-48 z-10">
                        User stories across all projects and statuses
                      </div>
                    </div>
                  </div>
                  {isLoading ? (
                    <div className="h-9 bg-green-200 rounded animate-pulse mb-1"></div>
                  ) : (
                    <p className="text-3xl font-bold text-green-700 dark:text-green-200 animate-in fade-in-50 duration-1000 delay-200">
                      {analytics.summary.total_stories}
                    </p>
                  )}
                  <p className="text-xs text-green-500 mt-1 animate-in slide-in-from-bottom-2 duration-700 delay-400">
                    User Stories
                  </p>
                </div>
                <div className="p-3 bg-green-500 rounded-full animate-in scale-in-75 duration-500 delay-500">
                  <CheckSquare className="w-6 h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-800">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-red-600 dark:text-red-300">Total Defects</p>
                  <p className="text-3xl font-bold text-red-700 dark:text-red-200">{analytics.summary.total_defects}</p>
                  <p className="text-xs text-red-500 mt-1">Bug Reports</p>
                </div>
                <div className="p-3 bg-red-500 rounded-full">
                  <Bug className="w-6 h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-600 dark:text-purple-300">Team Members</p>
                  <p className="text-3xl font-bold text-purple-700 dark:text-purple-200">{analytics.summary.total_assignees}</p>
                  <p className="text-xs text-purple-500 mt-1">Active Contributors</p>
                </div>
                <div className="p-3 bg-purple-500 rounded-full">
                  <Users className="w-6 h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Velocity Chart */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-blue-500 animate-pulse" />
                <span>Sprint Velocity Trend</span>
              </CardTitle>
              <CardDescription>Story points completed vs planned over time</CardDescription>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="h-80 flex items-end justify-between space-x-3 px-4 overflow-hidden">
                {velocityData.map((sprint, index) => (
                  <div key={index} className="flex flex-col items-center space-y-3 flex-1 group">
                    <div className="w-full flex flex-col space-y-1 relative">
                      <div className="relative">
                        <div 
                          className="bg-gradient-to-t from-blue-600 to-blue-400 rounded-t transition-all duration-1000 ease-out hover:from-blue-700 hover:to-blue-500"
                          style={{ 
                            height: `${(sprint.completed / 60) * 250}px`,
                            animationDelay: `${index * 200}ms`
                          }}
                        />
                        <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                          Completed: {sprint.completed}
                        </div>
                      </div>
                      <div className="relative">
                        <div 
                          className="bg-gradient-to-t from-gray-400 to-gray-300 dark:from-gray-600 dark:to-gray-500 rounded-b transition-all duration-1000 ease-out hover:from-gray-500 hover:to-gray-400"
                          style={{ 
                            height: `${(sprint.planned / 60) * 250}px`,
                            animationDelay: `${index * 200 + 100}ms`
                          }}
                        />
                        <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-gray-700 text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                          Planned: {sprint.planned}
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 text-center space-y-1">
                      <div className="font-medium text-sm">{sprint.sprint}</div>
                      <div className="text-blue-500 font-semibold">{sprint.completed}</div>
                      <div className="text-gray-500">{sprint.planned}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex justify-center space-x-6 mt-6 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-blue-400 rounded animate-pulse"></div>
                  <span className="font-medium">Completed</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-r from-gray-400 to-gray-300 dark:from-gray-600 dark:to-gray-500 rounded animate-pulse"></div>
                  <span className="font-medium">Planned</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Top Performer Highlight */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center space-x-2">
                <Target className="w-5 h-5 text-green-500 animate-pulse" />
                <span>Top Performer</span>
              </CardTitle>
              <CardDescription>Highest velocity contributor this period</CardDescription>
            </CardHeader>
            <CardContent className="pt-0 pb-6">
              {(() => {
                const top = teamPerformance.reduce((a, b) => (a.velocity >= b.velocity ? a : b))
                return (
                  <div className="flex items-center space-x-5 p-4 rounded-lg bg-gray-50 dark:bg-gray-800/40">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                      {top.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-base text-gray-900 dark:text-white">{top.name}</span>
                        <Badge className="bg-green-600 hover:bg-green-600">Velocity {top.velocity}</Badge>
                      </div>
                      <div className="mt-2 grid grid-cols-3 gap-3 text-xs">
                        <div className="flex items-center space-x-2">
                          <div className="w-2.5 h-2.5 bg-green-500 rounded-full"></div>
                          <span>{top.stories} stories</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-2.5 h-2.5 bg-red-500 rounded-full"></div>
                          <span>{top.defects} defects</span>
                        </div>
                        <div className="text-gray-500">Consistent high throughput</div>
                      </div>
                    </div>
                  </div>
                )
              })()}
            </CardContent>
          </Card>
        </div>

        {/* AI Insights & Projections */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-purple-500" />
              <span>AI Insights & Projections</span>
            </CardTitle>
            <CardDescription>Forward-looking analysis based on recent trends</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm text-gray-800 dark:text-gray-200">
              Velocity trend is <span className={`${velocityTrend === 'upward' ? 'text-green-600' : velocityTrend === 'downward' ? 'text-red-600' : 'text-gray-500'}`}>{velocityTrend}</span> with an average change of {averageVelocityDelta.toFixed(1)} points per sprint. If this persists, next sprint is projected at <span className="font-semibold">{projectedNextVelocity}</span> completed points.
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Current defect ratio is {defectRatio.toFixed(1)}%. {defectRatio > 40 ? 'High defects may impact delivery; consider quality focus.' : 'Defect ratio is manageable; maintain quality controls.'}
            </div>
            <div className="flex space-x-2 text-xs">
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Projection</Badge>
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Velocity</Badge>
              <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Quality</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Project Distribution Chart */}
        <Card className="overflow-hidden">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-orange-500 animate-pulse" />
              <span>Project Distribution</span>
            </CardTitle>
            <CardDescription>Issue breakdown across all projects</CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projectDistribution.map((project, index) => {
                const total = project.stories + project.defects + project.tasks
                return (
                  <div 
                    key={index} 
                    className="p-5 border rounded-xl hover:shadow-lg transition-shadow duration-300 group bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-bold text-lg text-gray-900 dark:text-white">{project.name}</h4>
                      <Badge variant="outline" className="bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300 px-3 py-1">
                        {total} total
                      </Badge>
                    </div>
                    <div className="space-y-3 mb-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">Stories</span>
                        <span className="font-bold text-green-600 text-lg">{project.stories}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">Defects</span>
                        <span className="font-bold text-red-600 text-lg">{project.defects}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">Tasks</span>
                        <span className="font-bold text-blue-600 text-lg">{project.tasks}</span>
                      </div>
                    </div>
                    <div className="mt-4 bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                      <div className="flex h-4 rounded-full overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-green-500 to-green-400 transition-all duration-1000 ease-out hover:from-green-600 hover:to-green-500"
                          style={{ 
                            width: `${(project.stories / total) * 100}%`,
                            animationDelay: `${index * 150}ms`
                          }}
                        />
                        <div 
                          className="bg-gradient-to-r from-red-500 to-red-400 transition-all duration-1000 ease-out hover:from-red-600 hover:to-red-500"
                          style={{ 
                            width: `${(project.defects / total) * 100}%`,
                            animationDelay: `${index * 150 + 100}ms`
                          }}
                        />
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-blue-400 transition-all duration-1000 ease-out hover:from-blue-600 hover:to-blue-500"
                          style={{ 
                            width: `${(project.tasks / total) * 100}%`,
                            animationDelay: `${index * 150 + 200}ms`
                          }}
                        />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Sprint Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-4">
          <Card className="bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-yellow-200 dark:border-yellow-800 hover:shadow-lg transition-shadow duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-4 bg-yellow-500 rounded-full animate-pulse">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-yellow-600 dark:text-yellow-300">Avg Velocity</p>
                  <p className="text-3xl font-bold text-yellow-700 dark:text-yellow-200 animate-bounce">47.2</p>
                  <p className="text-xs text-yellow-500 mt-1">Story Points/Sprint</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 border-indigo-200 dark:border-indigo-800 hover:shadow-lg transition-shadow duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-4 bg-indigo-500 rounded-full animate-pulse">
                  <Calendar className="w-8 h-8 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-indigo-600 dark:text-indigo-300">Sprint Duration</p>
                  <p className="text-3xl font-bold text-indigo-700 dark:text-indigo-200 animate-bounce">2 Weeks</p>
                  <p className="text-xs text-indigo-500 mt-1">Current Sprint Cycle</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 border-emerald-200 dark:border-emerald-800 hover:shadow-lg transition-shadow duration-300">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-4 bg-emerald-500 rounded-full animate-pulse">
                  <Award className="w-8 h-8 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-emerald-600 dark:text-emerald-300">Success Rate</p>
                  <p className="text-3xl font-bold text-emerald-700 dark:text-emerald-200 animate-bounce">94.2%</p>
                  <p className="text-xs text-emerald-500 mt-1">Sprint Completion</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI-Powered Strategic Insights Section */}
        {strategicInsights && (
          <Card className="border-0 shadow-xl bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-indigo-900/20 dark:via-purple-900/20 dark:to-pink-900/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-600 animate-pulse" />
                AI-Powered Strategic Insights
              </CardTitle>
              <CardDescription>
                Intelligent analysis and recommendations powered by OpenAI
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* AI Analysis */}
              <div className="p-4 rounded-lg bg-white/50 dark:bg-gray-900/50 border border-indigo-200 dark:border-indigo-800">
                <div className="flex items-start gap-3">
                  <Target className="h-6 w-6 text-indigo-600 mt-1 flex-shrink-0" />
                  <div className="text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-line">
                    {strategicInsights.ai_analysis}
                  </div>
                </div>
              </div>

              {/* Risk Assessment */}
              {strategicInsights.risk_assessment && strategicInsights.risk_assessment.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    Risk Assessment
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {strategicInsights.risk_assessment.map((risk, index) => (
                      <Card key={index} className="border-l-4 border-l-red-500">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-2">
                            <Badge variant={getRiskColor(risk.type)} className="capitalize">
                              {risk.type} Risk
                            </Badge>
                          </div>
                          <h5 className="font-medium mb-2">{risk.description}</h5>
                          <p className="text-sm text-muted-foreground mb-2">{risk.impact}</p>
                          <p className="text-sm font-medium text-blue-600 dark:text-blue-400">
                            💡 {risk.recommendation}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Opportunities */}
              {strategicInsights.opportunities && strategicInsights.opportunities.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Zap className="h-4 w-4 text-green-600" />
                    Growth Opportunities
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {strategicInsights.opportunities.map((opportunity, index) => (
                      <Card key={index} className="border-l-4 border-l-green-500">
                        <CardContent className="p-4">
                          <h5 className="font-medium mb-2">{opportunity.title}</h5>
                          <p className="text-sm text-muted-foreground mb-2">{opportunity.description}</p>
                          <p className="text-sm font-medium text-green-600 dark:text-green-400">
                            🎯 {opportunity.potential_impact}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Key Recommendations */}
              {strategicInsights.key_recommendations && strategicInsights.key_recommendations.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Target className="h-4 w-4 text-purple-600" />
                    Key Recommendations
                  </h4>
                  <div className="space-y-3">
                    {strategicInsights.key_recommendations.map((rec, index) => (
                      <Card key={index} className="border-l-4 border-l-purple-500">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <Badge variant={getPriorityColor(rec.priority)} className="capitalize">
                              {rec.priority} Priority
                            </Badge>
                            <span className="text-sm text-muted-foreground">{rec.timeline}</span>
                          </div>
                          <h5 className="font-medium mb-2">{rec.action}</h5>
                          <p className="text-sm text-muted-foreground">
                            Expected outcome: {rec.expected_outcome}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}