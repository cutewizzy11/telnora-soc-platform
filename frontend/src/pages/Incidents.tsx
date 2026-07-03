import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import SeverityBadge from "../components/SeverityBadge";

interface Incident {
  id: string;
  title: string;
  severity: string;
  status: string;
  created_at: string;
}

const COLUMNS = [
  { key: "open", label: "Open" },
  { key: "in_progress", label: "In Progress" },
  { key: "contained", label: "Contained" },
  { key: "resolved", label: "Resolved" },
  { key: "closed", label: "Closed" },
];

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  const load = async () => {
    const resp = await client.get("/incidents");
    setIncidents(resp.data);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-white">Incidents</h1>
        <p className="text-sm text-slate-400">Case management board for active security incidents.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {COLUMNS.map((col) => (
          <div key={col.key} className="card min-h-[300px]">
            <h2 className="text-xs uppercase tracking-wide text-slate-400 mb-3">{col.label}</h2>
            <div className="space-y-2">
              {incidents
                .filter((i) => i.status === col.key)
                .map((i) => (
                  <Link
                    to={`/incidents/${i.id}`}
                    key={i.id}
                    className="block bg-slate-900 border border-slate-800 rounded-lg p-3 hover:border-telnora-accent/60 transition-colors"
                  >
                    <div className="text-sm text-slate-200 mb-2">{i.title}</div>
                    <SeverityBadge severity={i.severity} />
                  </Link>
                ))}
              {incidents.filter((i) => i.status === col.key).length === 0 && (
                <div className="text-xs text-slate-600">No incidents</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
