import React, { useEffect, useState } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import client from "../api/client";
import StatCard from "../components/StatCard";

interface Summary {
  total_alerts: number;
  open_alerts: number;
  open_incidents: number;
  total_iocs: number;
  alerts_by_severity: Record<string, number>;
  alerts_by_status: Record<string, number>;
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#3b82f6",
  info: "#64748b",
};

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [mttd, setMttd] = useState<any>(null);
  const [mttr, setMttr] = useState<any>(null);

  useEffect(() => {
    client.get("/analytics/summary").then((r) => setSummary(r.data));
    client.get("/analytics/mttd").then((r) => setMttd(r.data));
    client.get("/analytics/mttr").then((r) => setMttr(r.data));
  }, []);

  if (!summary) return <div className="text-slate-400 text-sm">Loading dashboard...</div>;

  const pieData = Object.entries(summary.alerts_by_severity).map(([k, v]) => ({ name: k, value: v }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-white">SOC Dashboard</h1>
        <p className="text-sm text-slate-400">Real-time overview of alerts, incidents, and threat intel.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Alerts" value={summary.total_alerts} />
        <StatCard label="Open Alerts" value={summary.open_alerts} />
        <StatCard label="Open Incidents" value={summary.open_incidents} />
        <StatCard label="Threat Intel IOCs" value={summary.total_iocs} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card md:col-span-1">
          <h2 className="text-sm font-medium text-slate-300 mb-2">Alerts by Severity</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={80} paddingAngle={2}>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={SEVERITY_COLORS[entry.name] ?? "#64748b"} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e293b" }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="text-sm font-medium text-slate-300 mb-3">Mean Time to Triage (MTTD)</h2>
          <div className="text-3xl font-semibold text-white">
            {mttd?.mean_minutes != null ? `${mttd.mean_minutes} min` : "—"}
          </div>
          <div className="text-xs text-slate-500 mt-1">Sample size: {mttd?.sample_size ?? 0} alerts</div>
        </div>

        <div className="card">
          <h2 className="text-sm font-medium text-slate-300 mb-3">Mean Time to Resolve (MTTR)</h2>
          <div className="text-3xl font-semibold text-white">
            {mttr?.mean_minutes != null ? `${mttr.mean_minutes} min` : "—"}
          </div>
          <div className="text-xs text-slate-500 mt-1">Sample size: {mttr?.sample_size ?? 0} incidents</div>
        </div>
      </div>
    </div>
  );
}
