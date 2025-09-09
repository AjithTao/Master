export function KpiCards({ completion, defect, capacity }: { completion?: number|null; defect?: number|null; capacity?: number|null }) {
  return (
    <div className="grid md:grid-cols-3 gap-4">
      <div className="rounded-2xl p-4 bg-white text-slate-900 dark:bg-card dark:text-card-foreground shadow border border-slate-200/50 dark:border-border">
        <div className="text-sm text-slate-500 dark:text-muted-foreground">Completion</div>
        <div className="text-2xl font-semibold">{completion != null ? `${completion}%` : "—"}</div>
      </div>
      <div className="rounded-2xl p-4 bg-white text-slate-900 dark:bg-card dark:text-card-foreground shadow border border-slate-200/50 dark:border-border">
        <div className="text-sm text-slate-500 dark:text-muted-foreground">Defect Ratio</div>
        <div className="text-2xl font-semibold">{defect != null ? `${defect}%` : "—"}</div>
      </div>
      <div className="rounded-2xl p-4 bg-white text-slate-900 dark:bg-card dark:text-card-foreground shadow border border-slate-200/50 dark:border-border">
        <div className="text-sm text-slate-500 dark:text-muted-foreground">Capacity Baseline</div>
        <div className="text-2xl font-semibold">{capacity != null ? capacity : "—"}</div>
      </div>
    </div>
  );
}