'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'

type Completed = { count: number; trend: { delta: number; percent: number } }
type Blockers = { total: number; by_priority: Record<string, number> }
type Contributors = { window_days: number; leaders: { name: string; closed: number }[] }
type Resolution = { avg_days: number; sample: number }
type Velocity = { current: number; previous: number; change_percent: number }

export function DashboardPage() {
  const [project, setProject] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [completed, setCompleted] = useState<Completed | null>(null)
  const [blockers, setBlockers] = useState<Blockers | null>(null)
  const [contributors, setContributors] = useState<Contributors | null>(null)
  const [resolution, setResolution] = useState<Resolution | null>(null)
  const [velocity, setVelocity] = useState<Velocity | null>(null)
  const [insight, setInsight] = useState<string>('')

  const fetchMetrics = async () => {
    setLoading(true)
    try {
      const body = (p?: object) => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p || {}) })
      const payload = project ? { project } : {}

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
    fetchMetrics()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <Input placeholder="Project key (optional, e.g., CCM)" value={project} onChange={(e) => setProject(e.target.value.toUpperCase())} className="w-64" />
        <Button onClick={fetchMetrics} disabled={loading}>{loading ? 'Loading…' : 'Refresh'}</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-sm">✅ Completed</div>
            <div className="text-2xl font-semibold">{completed?.count ?? '-'}</div>
            <div className={`text-sm ${((completed?.trend.percent || 0) >= 0) ? 'text-green-600' : 'text-red-600'}`}>
              {completed ? `${completed.trend.percent >= 0 ? '↑' : '↓'} ${Math.abs(completed.trend.percent)}%` : ''}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-sm">🛑 Blockers</div>
            <div className="text-2xl font-semibold">{blockers?.total ?? '-'}</div>
            <div className="text-xs text-muted-foreground">{blockers ? Object.entries(blockers.by_priority).map(([k,v]) => `${k}:${v}`).join(', ') : ''}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-sm">⚡ Top Contributors</div>
            <div className="text-sm">{contributors ? contributors.leaders.map(l => `${l.name} (${l.closed})`).join(', ') : '-'}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-sm">⏳ Avg Resolution</div>
            <div className="text-2xl font-semibold">{resolution?.avg_days ?? '-'} days</div>
            <div className="text-xs text-muted-foreground">sample: {resolution?.sample ?? '-'}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-sm">📉 Regression vs Prior Sprint</div>
            <div className="text-2xl font-semibold">{velocity ? `${velocity.current} vs ${velocity.previous}` : '-'}</div>
            <div className={`text-sm ${((velocity?.change_percent || 0) >= 0) ? 'text-green-600' : 'text-red-600'}`}>
              {velocity ? `${velocity.change_percent >= 0 ? '↑' : '↓'} ${Math.abs(velocity.change_percent)}%` : ''}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="text-sm mb-2">AI Insight</div>
          <div className="text-gray-800 dark:text-foreground whitespace-pre-line">{insight || '—'}</div>
        </CardContent>
      </Card>
    </div>
  )
}


