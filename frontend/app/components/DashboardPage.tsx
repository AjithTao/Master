'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
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
  Zap
} from 'lucide-react'

type Completed = { count: number; trend: { delta: number; percent: number } }
type Blockers = { total: number; by_priority: Record<string, number> }
type Contributors = { window_days: number; leaders: { name: string; closed: number }[] }
type Resolution = { avg_days: number; sample: number }
type Velocity = { current: number; previous: number; change_percent: number }

export function DashboardPage() {
  const [project, setProject] = useState<string>('ALL')
  const [availableProjects, setAvailableProjects] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [completed, setCompleted] = useState<Completed | null>(null)
  const [blockers, setBlockers] = useState<Blockers | null>(null)
  const [contributors, setContributors] = useState<Contributors | null>(null)
  const [resolution, setResolution] = useState<Resolution | null>(null)
  const [velocity, setVelocity] = useState<Velocity | null>(null)
  const [insight, setInsight] = useState<string>('')

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

  const fetchMetrics = async () => {
    setLoading(true)
    try {
      const body = (p?: object) => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p || {}) })
      const payload = project && project !== 'ALL' ? { project_key: project } : {}

      const [cRes, bRes, tRes, rRes, vRes] = await Promise.all([
        fetch('http://localhost:8000/api/metrics/completed', body(payload)),
        fetch('http://localhost:8000/api/metrics/blockers', body(payload)),
        fetch('http://localhost:8000/api/metrics/contributors', body(payload)),
        fetch('http://localhost:8000/api/metrics/resolution', body(payload)),
        fetch('http://localhost:8000/api/metrics/velocity', body(payload)),
      ])

      const [c, b, t, r, v] = await Promise.all([cRes.json(), bRes.json(), tRes.json(), rRes.json(), vRes.json()])
      setCompleted(c)
      setBlockers(b)
      setContributors(t)
      setResolution(r)
      setVelocity(v)

      const sumRes = await fetch('http://localhost:8000/api/metrics/summary', body({ project, completed: c, blockers: b, contributors: t, resolution: r, velocity: v }))
      const sum = await sumRes.json()
      setInsight(sum?.insight || '')
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (availableProjects.length > 0 || project === 'ALL') {
      fetchMetrics()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [project])

  return (
    <div className="space-y-4">
      <div className="flex flex-col space-y-4">
        {/* Project Filter */}
        <div className="flex flex-col space-y-2">
          <h3 className="text-sm font-medium">Project Filter:</h3>
          <div className="flex flex-wrap gap-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="radio"
                name="project"
                value="ALL"
                checked={project === 'ALL'}
                onChange={(e) => setProject(e.target.value)}
                className="text-blue-600"
              />
              <Badge variant={project === 'ALL' ? 'default' : 'outline'}>All Projects</Badge>
            </label>
            {availableProjects.map((proj) => (
              <label key={proj.key} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="project"
                  value={proj.key}
                  checked={project === proj.key}
                  onChange={(e) => setProject(e.target.value)}
                  className="text-blue-600"
                />
                <Badge variant={project === proj.key ? 'default' : 'outline'}>
                  {proj.key} - {proj.name}
                </Badge>
              </label>
            ))}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button onClick={fetchMetrics} disabled={loading}>{loading ? 'Loading…' : 'Refresh'}</Button>
          <span className="text-sm text-gray-500">
            {project === 'ALL' ? 'Showing metrics for all projects' : `Showing metrics for ${project}`}
          </span>
        </div>
      </div>

      {/* Animated Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Completed Stories/Bugs Card */}
        <Card className={`transition-all duration-500 hover:shadow-lg hover:scale-105 ${loading ? 'animate-pulse' : 'animate-in slide-in-from-bottom-4'}`}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              Completed Items
            </CardTitle>
            <div className="group relative">
              <Info className="h-4 w-4 text-gray-400 cursor-help" />
              <div className="absolute right-0 top-6 hidden group-hover:block bg-black text-white text-xs rounded p-2 w-64 z-10">
                <strong>How it's calculated:</strong><br/>
                • Stories + Bugs marked as "Done" or "Closed"<br/>
                • Trend compares last 7 days vs previous 7 days<br/>
                • Includes all issue types except Epics
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600 mb-2 transition-all duration-700">
              {loading ? (
                <div className="h-9 bg-gray-200 rounded animate-pulse"></div>
              ) : (
                <span className="animate-in fade-in-50 duration-1000">
                  {completed?.count ?? 0}
                </span>
              )}
            </div>
            <div className={`flex items-center gap-1 text-sm transition-all duration-500 ${
              (completed?.trend.percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {completed && (
                <>
                  {completed.trend.percent >= 0 ? (
                    <TrendingUp className="h-4 w-4 animate-bounce" />
                  ) : (
                    <TrendingDown className="h-4 w-4 animate-bounce" />
                  )}
                  <span className="animate-in slide-in-from-right-2 duration-700">
                    {Math.abs(completed.trend.percent)}% vs last week
                  </span>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Blockers Card */}
        <Card className={`transition-all duration-500 hover:shadow-lg hover:scale-105 ${loading ? 'animate-pulse' : 'animate-in slide-in-from-bottom-4 delay-150'}`}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              Active Blockers
            </CardTitle>
            <div className="group relative">
              <Info className="h-4 w-4 text-gray-400 cursor-help" />
              <div className="absolute right-0 top-6 hidden group-hover:block bg-black text-white text-xs rounded p-2 w-64 z-10">
                <strong>How it's calculated:</strong><br/>
                • Issues with "Blocked" status or "blocker" label<br/>
                • Grouped by priority: Highest, High, Medium, Low<br/>
                • Real-time count of unresolved blockers
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600 mb-2 transition-all duration-700">
              {loading ? (
                <div className="h-9 bg-gray-200 rounded animate-pulse"></div>
              ) : (
                <span className="animate-in fade-in-50 duration-1000 delay-300">
                  {blockers?.total ?? 0}
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-1">
              {blockers && Object.entries(blockers.by_priority).map(([priority, count], index) => (
                <Badge 
                  key={priority} 
                  variant={count > 0 ? "destructive" : "outline"}
                  className={`text-xs animate-in slide-in-from-bottom-2 duration-500 delay-${index * 100 + 400}`}
                >
                  {priority}: {count}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Contributors Card */}
        <Card className={`transition-all duration-500 hover:shadow-lg hover:scale-105 ${loading ? 'animate-pulse' : 'animate-in slide-in-from-bottom-4 delay-300'}`}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-600" />
              Top Contributors
            </CardTitle>
            <div className="group relative">
              <Info className="h-4 w-4 text-gray-400 cursor-help" />
              <div className="absolute right-0 top-6 hidden group-hover:block bg-black text-white text-xs rounded p-2 w-64 z-10">
                <strong>How it's calculated:</strong><br/>
                • Based on completed items in last {contributors?.window_days || 30} days<br/>
                • Ranked by total closed stories + bugs<br/>
                • Updates daily with fresh data
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {loading ? (
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                  <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                </div>
              ) : (
                contributors?.leaders.slice(0, 3).map((leader, index) => (
                  <div 
                    key={leader.name}
                    className={`flex items-center justify-between animate-in slide-in-from-left-4 duration-500 delay-${index * 150 + 500}`}
                  >
                    <span className="text-sm font-medium">{leader.name}</span>
                    <Badge variant="secondary" className="animate-in fade-in-50 duration-700">
                      {leader.closed} items
                    </Badge>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Average Resolution Time Card */}
        <Card className={`transition-all duration-500 hover:shadow-lg hover:scale-105 ${loading ? 'animate-pulse' : 'animate-in slide-in-from-left-4 delay-500'}`}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4 text-orange-600" />
              Average Resolution Time
            </CardTitle>
            <div className="group relative">
              <Info className="h-4 w-4 text-gray-400 cursor-help" />
              <div className="absolute right-0 top-6 hidden group-hover:block bg-black text-white text-xs rounded p-2 w-64 z-10">
                <strong>How it's calculated:</strong><br/>
                • Time from "In Progress" to "Done" status<br/>
                • Excludes weekends and holidays<br/>
                • Based on last {resolution?.sample || 50} completed items<br/>
                • Weighted average across all issue types
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600 mb-2 transition-all duration-700">
              {loading ? (
                <div className="h-9 bg-gray-200 rounded animate-pulse"></div>
              ) : (
                <span className="animate-in fade-in-50 duration-1000 delay-600">
                  {resolution?.avg_days ?? 0}
                </span>
              )}
              <span className="text-lg text-gray-500 ml-1">days</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <BarChart3 className="h-4 w-4" />
              <span className="animate-in slide-in-from-right-2 duration-700 delay-700">
                Sample size: {resolution?.sample ?? 0} items
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Velocity Comparison Card */}
        <Card className={`transition-all duration-500 hover:shadow-lg hover:scale-105 ${loading ? 'animate-pulse' : 'animate-in slide-in-from-right-4 delay-500'}`}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Target className="h-4 w-4 text-purple-600" />
              Sprint Velocity
            </CardTitle>
            <div className="group relative">
              <Info className="h-4 w-4 text-gray-400 cursor-help" />
              <div className="absolute right-0 top-6 hidden group-hover:block bg-black text-white text-xs rounded p-2 w-64 z-10">
                <strong>How it's calculated:</strong><br/>
                • Story points completed in current vs previous sprint<br/>
                • Current: {velocity?.current || 0} points<br/>
                • Previous: {velocity?.previous || 0} points<br/>
                • Percentage change indicates team acceleration/deceleration
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 mb-2">
              <div className="text-3xl font-bold text-purple-600 transition-all duration-700">
                {loading ? (
                  <div className="h-9 bg-gray-200 rounded animate-pulse"></div>
                ) : (
                  <span className="animate-in fade-in-50 duration-1000 delay-600">
                    {velocity?.current ?? 0}
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-500">
                vs {velocity?.previous ?? 0}
              </div>
            </div>
            <div className={`flex items-center gap-1 text-sm transition-all duration-500 ${
              (velocity?.change_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {velocity && (
                <>
                  {velocity.change_percent >= 0 ? (
                    <TrendingUp className="h-4 w-4 animate-bounce" />
                  ) : (
                    <TrendingDown className="h-4 w-4 animate-bounce" />
                  )}
                  <span className="animate-in slide-in-from-left-2 duration-700 delay-700">
                    {Math.abs(velocity.change_percent)}% vs previous sprint
                  </span>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights Card */}
      <Card className={`transition-all duration-500 hover:shadow-lg ${loading ? 'animate-pulse' : 'animate-in slide-in-from-bottom-4 delay-700'}`}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-600 animate-pulse" />
            AI-Powered Leadership Insights
          </CardTitle>
          <div className="group relative">
            <Info className="h-4 w-4 text-gray-400 cursor-help" />
            <div className="absolute right-0 top-6 hidden group-hover:block bg-black text-white text-xs rounded p-2 w-64 z-10">
              <strong>How it's generated:</strong><br/>
              • OpenAI analyzes all the metrics above<br/>
              • Identifies patterns, trends, and risks<br/>
              • Provides actionable leadership recommendations<br/>
              • Updates in real-time with fresh data
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
            </div>
          ) : (
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-lg border-l-4 border-indigo-500">
              <div className="flex items-start gap-3">
                <Zap className="h-5 w-5 text-indigo-600 mt-0.5 flex-shrink-0" />
                <div className="text-gray-800 dark:text-foreground whitespace-pre-line animate-in fade-in-50 duration-1000 delay-800">
                  {insight || 'Analyzing team performance and generating insights... Please refresh to see AI recommendations.'}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


