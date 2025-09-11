"use client"

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Alert, AlertDescription, AlertTitle } from './ui/alert'
import { Progress } from './ui/progress'
import { Separator } from './ui/separator'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Users, 
  BarChart3, 
  Info,
  Sparkles,
  Target,
  Zap,
  Download,
  RefreshCw,
  Activity,
  Award,
  Calendar,
  FolderOpen,
  Bug,
  FileText,
  AlertCircle,
  ChevronRight,
  Crown,
  Shield,
  Star,
  ArrowUpRight,
  ArrowDownRight,
  Loader2
} from 'lucide-react'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

interface DashboardMetrics {
  portfolio_summary: {
    total_projects: number
    total_issues: number
    completed_items: number
    completion_rate: number
    active_contributors: number
  }
  project_health: {
    [key: string]: {
      name: string
      health_score: number
      status: 'excellent' | 'good' | 'needs_attention' | 'critical'
      total_issues: number
      completed: number
      in_progress: number
      blocked: number
      velocity_trend: 'up' | 'down' | 'stable'
    }
  }
  team_performance: {
    top_performers: Array<{
      name: string
      completed_items: number
      efficiency_score: number
      workload_balance: 'optimal' | 'heavy' | 'light'
    }>
    workload_distribution: {
      balanced: number
      overloaded: number
      underutilized: number
    }
    capacity_utilization: number
  }
  quality_metrics: {
    defect_rate: number
    resolution_time: {
      average_days: number
      trend: 'improving' | 'declining' | 'stable'
    }
    customer_satisfaction: number
    technical_debt_score: number
  }
  strategic_insights: {
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
  generated_at: string
}

export function EnhancedLeadershipDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedProject, setSelectedProject] = useState<string>('ALL')
  const [availableProjects, setAvailableProjects] = useState<any[]>([])
  const [isExporting, setIsExporting] = useState(false)
  const dashboardRef = useRef<HTMLDivElement>(null)

  // Fetch available projects
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

  // Fetch dashboard metrics with AI insights
  const fetchDashboardMetrics = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const endpoint = selectedProject === 'ALL' 
        ? 'http://localhost:8000/api/leadership/dashboard'
        : `http://localhost:8000/api/leadership/dashboard?project=${selectedProject}`
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          include_ai_insights: true,
          detailed_analysis: true 
        })
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        setMetrics(data.dashboard)
      } else {
        setError(data.error || 'Failed to fetch dashboard metrics')
      }
    } catch (error) {
      setError('Network error: ' + (error instanceof Error ? error.message : 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  // Export to PDF with proper formatting
  const exportToPDF = async () => {
    if (!dashboardRef.current) return
    
    setIsExporting(true)
    try {
      const element = dashboardRef.current
      
      // Temporarily adjust for PDF export
      element.style.width = '1200px'
      element.style.backgroundColor = '#ffffff'
      
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        width: 1200,
        height: element.scrollHeight,
        scrollX: 0,
        scrollY: 0
      })
      
      const imgData = canvas.toDataURL('image/png')
      const pdf = new jsPDF('p', 'mm', 'a4')
      
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = pdf.internal.pageSize.getHeight()
      const imgWidth = pdfWidth - 20 // 10mm margin on each side
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      
      let heightLeft = imgHeight
      let position = 10 // 10mm top margin
      
      // Add title page
      pdf.setFontSize(24)
      pdf.text('Leadership Dashboard Report', pdfWidth / 2, 30, { align: 'center' })
      pdf.setFontSize(12)
      pdf.text(`Generated: ${new Date().toLocaleString()}`, pdfWidth / 2, 40, { align: 'center' })
      pdf.text(`Project Filter: ${selectedProject}`, pdfWidth / 2, 50, { align: 'center' })
      
      // Add first page of content
      pdf.addImage(imgData, 'PNG', 10, 60, imgWidth, Math.min(imgHeight, pdfHeight - 70))
      heightLeft -= (pdfHeight - 70)
      
      // Add additional pages if needed
      while (heightLeft > 0) {
        pdf.addPage()
        position = -heightLeft + 10
        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight)
        heightLeft -= (pdfHeight - 20)
      }
      
      pdf.save(`leadership-dashboard-${selectedProject}-${new Date().toISOString().split('T')[0]}.pdf`)
      
      // Reset styles
      element.style.width = ''
      element.style.backgroundColor = ''
      
    } catch (error) {
      console.error('PDF export failed:', error)
      setError('PDF export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  useEffect(() => {
    fetchProjects()
    // Always fetch dashboard metrics on component mount
    fetchDashboardMetrics()
  }, [])

  useEffect(() => {
    // Fetch metrics when project selection changes
    fetchDashboardMetrics()
  }, [selectedProject])

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'text-green-600 bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800'
      case 'good': return 'text-blue-600 bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800'
      case 'needs_attention': return 'text-orange-600 bg-orange-50 border-orange-200 dark:bg-orange-900/20 dark:border-orange-800'
      case 'critical': return 'text-red-600 bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
      default: return 'text-gray-600 bg-gray-50 border-gray-200 dark:bg-gray-900/20 dark:border-gray-800'
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

  if (error) {
    return (
      <div className="p-6">
        <Alert className="border-red-200 bg-red-50 dark:bg-red-900/20">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Dashboard Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button onClick={fetchDashboardMetrics} className="mt-4">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 transition-colors duration-300 overflow-auto">
      <div className="container mx-auto p-3 sm:p-6 space-y-4 sm:space-y-6 max-w-7xl" ref={dashboardRef}>
        {/* Header Section */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Leadership Dashboard
            </h1>
            <p className="text-lg text-muted-foreground">
              AI-powered insights and strategic analytics for leadership decision making
            </p>
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            {/* Project Filter */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedProject === 'ALL' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedProject('ALL')}
                className="transition-all duration-200"
              >
                All Projects
              </Button>
              {availableProjects.map((project) => (
                <Button
                  key={project.key}
                  variant={selectedProject === project.key ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedProject(project.key)}
                  className="transition-all duration-200"
                >
                  {project.key}
                </Button>
              ))}
            </div>
            
            <Separator orientation="vertical" className="h-8" />
            
            {/* Action Buttons */}
            <Button
              onClick={fetchDashboardMetrics}
              disabled={loading}
              variant="outline"
              size="sm"
              className="transition-all duration-200"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Refresh
            </Button>
            
            <Button
              onClick={exportToPDF}
              disabled={isExporting || loading}
              size="sm"
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
            >
              {isExporting ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Download className="w-4 h-4 mr-2" />
              )}
              Export PDF
            </Button>
          </div>
        </div>

        {loading || !metrics ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : metrics ? (
          <>
            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3 sm:gap-4">
              <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-blue-200 dark:border-blue-800">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Projects</p>
                      <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                        {metrics?.portfolio_summary?.total_projects || 0}
                      </p>
                    </div>
                    <FolderOpen className="h-8 w-8 text-blue-500 group-hover:scale-110 transition-transform duration-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-green-200 dark:border-green-800">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Issues</p>
                      <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                        {metrics?.portfolio_summary?.total_issues || 0}
                      </p>
                    </div>
                    <FileText className="h-8 w-8 text-green-500 group-hover:scale-110 transition-transform duration-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-purple-200 dark:border-purple-800">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Completed</p>
                      <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                        {metrics?.portfolio_summary?.completed_items || 0}
                      </p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-purple-500 group-hover:scale-110 transition-transform duration-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-orange-200 dark:border-orange-800">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Completion Rate</p>
                      <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                        {metrics?.portfolio_summary?.completion_rate || 0}%
                      </p>
                    </div>
                    <Target className="h-8 w-8 text-orange-500 group-hover:scale-110 transition-transform duration-200" />
                  </div>
                  <Progress 
                    value={metrics?.portfolio_summary?.completion_rate || 0} 
                    className="mt-2 h-2"
                  />
                </CardContent>
              </Card>

              <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-indigo-200 dark:border-indigo-800">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Contributors</p>
                      <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                        {metrics?.portfolio_summary?.active_contributors || 0}
                      </p>
                    </div>
                    <Users className="h-8 w-8 text-indigo-500 group-hover:scale-110 transition-transform duration-200" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Project Health Overview */}
            <Card className="border-0 shadow-lg bg-gradient-to-r from-white to-gray-50 dark:from-gray-900 dark:to-gray-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-blue-600" />
                  Project Health Overview
                </CardTitle>
                <CardDescription>
                  Real-time health assessment of all projects with AI-powered insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(metrics.project_health).map(([key, project]) => (
                    <Card key={key} className={`border transition-all duration-300 hover:shadow-md ${getHealthColor(project.status)}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="font-semibold text-lg">{project.name}</h3>
                          <Badge variant="outline" className="capitalize">
                            {project.status.replace('_', ' ')}
                          </Badge>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Health Score</span>
                            <span className="font-medium">{project.health_score}/100</span>
                          </div>
                          <Progress value={project.health_score} className="h-2" />
                          
                          <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
                            <div>
                              <span className="text-muted-foreground">Total: </span>
                              <span className="font-medium">{project.total_issues}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Done: </span>
                              <span className="font-medium text-green-600">{project.completed}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">In Progress: </span>
                              <span className="font-medium text-blue-600">{project.in_progress}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Blocked: </span>
                              <span className="font-medium text-red-600">{project.blocked}</span>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between mt-3 pt-3 border-t">
                            <span className="text-sm text-muted-foreground">Velocity</span>
                            <div className="flex items-center gap-1">
                              {project.velocity_trend === 'up' ? (
                                <ArrowUpRight className="h-4 w-4 text-green-600" />
                              ) : project.velocity_trend === 'down' ? (
                                <ArrowDownRight className="h-4 w-4 text-red-600" />
                              ) : (
                                <div className="h-4 w-4 rounded-full bg-gray-400"></div>
                              )}
                              <span className="text-sm font-medium capitalize">{project.velocity_trend}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Team Performance */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="h-5 w-5 text-yellow-600" />
                    Top Performers
                  </CardTitle>
                  <CardDescription>
                    Team members with highest productivity and efficiency scores
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {metrics?.team_performance?.top_performers?.map((performer, index) => (
                      <div key={performer.name} className="flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 transition-all duration-200 hover:shadow-md">
                        <div className="flex items-center gap-3">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r from-yellow-400 to-orange-400 text-white font-bold text-sm">
                            {index + 1}
                          </div>
                          <div>
                            <p className="font-medium">{performer.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {performer.completed_items} completed items
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={
                            performer.workload_balance === 'optimal' ? 'default' :
                            performer.workload_balance === 'heavy' ? 'destructive' : 'secondary'
                          }>
                            {performer.workload_balance}
                          </Badge>
                          <p className="text-sm text-muted-foreground mt-1">
                            {performer.efficiency_score}% efficiency
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-blue-600" />
                    Workload Distribution
                  </CardTitle>
                  <CardDescription>
                    Team capacity and workload balance analysis
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium">Capacity Utilization</span>
                        <span className="text-sm font-bold">{metrics?.team_performance?.capacity_utilization || 0}%</span>
                      </div>
                      <Progress value={metrics?.team_performance?.capacity_utilization || 0} className="h-3" />
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                        <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {metrics?.team_performance?.workload_distribution?.balanced || 0}
                        </div>
                        <div className="text-sm text-green-600 dark:text-green-400">Balanced</div>
                      </div>
                      
                      <div className="text-center p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                        <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                          {metrics?.team_performance?.workload_distribution?.overloaded || 0}
                        </div>
                        <div className="text-sm text-red-600 dark:text-red-400">Overloaded</div>
                      </div>
                      
                      <div className="text-center p-3 rounded-lg bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800">
                        <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                          {metrics?.team_performance?.workload_distribution?.underutilized || 0}
                        </div>
                        <div className="text-sm text-orange-600 dark:text-orange-400">Under-utilized</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quality Metrics */}
            <Card className="border-0 shadow-lg bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-purple-600" />
                  Quality Metrics
                </CardTitle>
                <CardDescription>
                  Quality indicators and technical health assessment
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">
                      {metrics?.quality_metrics?.defect_rate || 0}%
                    </div>
                    <div className="text-sm text-muted-foreground">Defect Rate</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                        {metrics?.quality_metrics?.resolution_time?.average_days || 0}
                      </div>
                      {metrics?.quality_metrics?.resolution_time?.trend === 'improving' ? (
                        <TrendingDown className="h-5 w-5 text-green-600" />
                      ) : metrics?.quality_metrics?.resolution_time?.trend === 'declining' ? (
                        <TrendingUp className="h-5 w-5 text-red-600" />
                      ) : (
                        <div className="h-5 w-5 rounded-full bg-gray-400"></div>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">Avg Resolution (days)</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">
                      {metrics?.quality_metrics?.customer_satisfaction || 0}%
                    </div>
                    <div className="text-sm text-muted-foreground">Customer Satisfaction</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-2">
                      {metrics?.quality_metrics?.technical_debt_score || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Technical Debt Score</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI-Powered Strategic Insights */}
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
                    <Crown className="h-6 w-6 text-indigo-600 mt-1 flex-shrink-0" />
                    <div className="text-gray-800 dark:text-gray-200 leading-relaxed">
                      {metrics?.strategic_insights?.ai_analysis || 'Loading AI analysis...'}
                    </div>
                  </div>
                </div>

                {/* Risk Assessment */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    Risk Assessment
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {metrics?.strategic_insights?.risk_assessment?.map((risk, index) => (
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

                {/* Opportunities */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Zap className="h-4 w-4 text-green-600" />
                    Growth Opportunities
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {metrics?.strategic_insights?.opportunities?.map((opportunity, index) => (
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

                {/* Key Recommendations */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Target className="h-4 w-4 text-purple-600" />
                    Key Recommendations
                  </h4>
                  <div className="space-y-3">
                    {metrics?.strategic_insights?.key_recommendations?.map((rec, index) => (
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
              </CardContent>
            </Card>

            {/* Footer */}
            <div className="text-center text-sm text-muted-foreground py-4">
              Last updated: {new Date(metrics.generated_at).toLocaleString()}
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}
