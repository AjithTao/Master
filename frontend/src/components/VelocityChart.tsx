import { ResponsiveContainer, ComposedChart, CartesianGrid, XAxis, YAxis, Tooltip, Bar, Line, Area, ReferenceLine } from "recharts";

export default function VelocityChart({
  series, proj, baseline
}: {
  series: { label: string; velocity: number }[];
  proj: { velocity_forecast_next: number; velocity_forecast_band: [number, number] };
  baseline?: number | null;
}) {
  const data = series.map(d => ({ name: d.label, velocity: d.velocity }));
  const next = {
    name: "Next",
    velocity: proj.velocity_forecast_next,
    low: proj.velocity_forecast_band[0],
    high: proj.velocity_forecast_band[1],
  };
  const all = [...data, next];

  return (
    <div className="rounded-2xl p-5 bg-white text-slate-900 dark:bg-card dark:text-card-foreground shadow-lg border border-slate-200/50 dark:border-border">
      <h3 className="text-lg font-semibold mb-3">Velocity (with projection)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={all}>
          <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.15} />
          <XAxis dataKey="name" stroke="currentColor" tick={{ fill: 'currentColor' }} />
          <YAxis stroke="currentColor" tick={{ fill: 'currentColor' }} />
          <Tooltip contentStyle={{ background: 'hsl(var(--card))', color: 'hsl(var(--card-foreground))', border: '1px solid hsl(var(--border))' }} />
          <Bar dataKey="velocity" fill="currentColor" />
          <Area dataKey="high" fill="currentColor" fillOpacity={0.08} stroke="none" />
          <Area dataKey="low" fill="currentColor" fillOpacity={0.08} stroke="none" />
          <Line type="monotone" dataKey="velocity" stroke="currentColor" />
          {baseline ? <ReferenceLine y={baseline} strokeDasharray="4 4" label={{ value: "Capacity", position: "right" }} /> : null}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}