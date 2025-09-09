import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";

export default function BandwidthChart({ data }: { data: Record<string, {issues:number; done:number; points?:number}> }) {
  const rows = Object.entries(data).map(([name, v]) => ({ name, Issues: v.issues, Done: v.done }));
  return (
    <div className="rounded-2xl p-5 bg-white text-slate-900 dark:bg-card dark:text-card-foreground shadow-lg border border-slate-200/50 dark:border-border">
      <h3 className="text-lg font-semibold mb-3">Bandwidth by Assignee</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={rows}>
          <XAxis dataKey="name" stroke="currentColor" tick={{ fill: 'currentColor' }} />
          <YAxis stroke="currentColor" tick={{ fill: 'currentColor' }} />
          <Tooltip contentStyle={{ background: 'hsl(var(--card))', color: 'hsl(var(--card-foreground))', border: '1px solid hsl(var(--border))' }} />
          <Legend wrapperStyle={{ color: 'currentColor' }} />
          <Bar dataKey="Issues" fill="currentColor" />
          <Bar dataKey="Done" fill="currentColor" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}