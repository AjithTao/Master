'use client'

import { useEffect, useState } from "react";
import VelocityChart from "../../src/components/VelocityChart";
import { KpiCards } from "../../src/components/KpiCards";
import BandwidthChart from "../../src/components/BandwidthChart";
import { Suggestions } from "../../src/components/Suggestions";

export default function Leadership() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const boardId = 123; // TODO: make this selectable

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
        const response = await fetch(`${backendUrl}/api/leadership/overview?board_id=${boardId}`);
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        console.error('Error fetching leadership data:', err);
        setError('Failed to load leadership data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [boardId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-muted-foreground">Loading leadership data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️</div>
          <p className="text-gray-600 dark:text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  if (!data?.success) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-yellow-500 text-xl mb-4">⚠️</div>
          <p className="text-gray-600 dark:text-muted-foreground">No data available</p>
        </div>
      </div>
    );
  }

  const d = data.data;
  const charts = d.charts;
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-background">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-foreground">Leadership Analysis</h1>
          <div className="text-sm text-gray-500 dark:text-muted-foreground">
            Board ID: {boardId}
          </div>
        </div>
        
        <KpiCards
          completion={charts.completion_rate}
          defect={charts.defect_ratio}
          capacity={charts.capacity_baseline}
        />
        
        <VelocityChart
          series={charts.velocity_series}
          proj={charts.projections}
          baseline={charts.capacity_baseline}
        />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BandwidthChart data={charts.bandwidth || {}} />
          <Suggestions items={d.suggestions || []} />
        </div>
      </div>
    </div>
  );
}
