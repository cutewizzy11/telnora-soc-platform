import React, { useEffect, useState } from "react";
import client from "../api/client";
import SeverityBadge from "../components/SeverityBadge";

export default function Analytics() {
  const [sla, setSla] = useState<any>(null);

  useEffect(() => {
    client.get("/analytics/sla").then((r) => setSla(r.data));
  }, []);

  if (!sla) return <div className="text-sm text-slate-400">Loading...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-white">Analytics & SLA Compliance</h1>
        <p className="text-sm text-slate-400">
          Percentage of alerts triaged within their severity's SLA window.
        </p>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-800">
              <th className="py-2 pr-4">Severity</th>
              <th className="py-2 pr-4">SLA target</th>
              <th className="py-2 pr-4">Total alerts</th>
              <th className="py-2 pr-4">Met SLA</th>
              <th className="py-2 pr-4">Compliance %</th>
              <th className="py-2 pr-4">Currently breached (open)</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(sla).map(([severity, data]: [string, any]) => (
              <tr key={severity} className="border-b border-slate-800/60">
                <td className="py-2 pr-4"><SeverityBadge severity={severity} /></td>
                <td className="py-2 pr-4 text-slate-400">{data.sla_minutes ?? "—"} min</td>
                <td className="py-2 pr-4 text-slate-300">{data.total}</td>
                <td className="py-2 pr-4 text-slate-300">{data.met_sla}</td>
                <td className="py-2 pr-4">
                  {data.pct != null ? (
                    <span className={data.pct >= 80 ? "text-emerald-400" : "text-orange-400"}>{data.pct}%</span>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="py-2 pr-4 text-red-400">{data.breached_open}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
