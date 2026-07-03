import React, { useEffect, useState } from "react";
import client from "../api/client";

export default function AuditLog() {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    client.get("/audit").then((r) => setLogs(r.data));
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-white">Audit Log</h1>
        <p className="text-sm text-slate-400">Every state-changing action taken across the platform.</p>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-800">
              <th className="py-2 pr-4">Time</th>
              <th className="py-2 pr-4">Actor</th>
              <th className="py-2 pr-4">Action</th>
              <th className="py-2 pr-4">Target</th>
              <th className="py-2 pr-4">Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.id} className="border-b border-slate-800/60">
                <td className="py-2 pr-4 text-slate-500 text-xs whitespace-nowrap">
                  {new Date(l.created_at).toLocaleString()}
                </td>
                <td className="py-2 pr-4 text-slate-300">{l.actor_email}</td>
                <td className="py-2 pr-4 text-telnora-accent text-xs">{l.action}</td>
                <td className="py-2 pr-4 text-slate-400 text-xs">
                  {l.target_type ? `${l.target_type}:${l.target_id}` : "—"}
                </td>
                <td className="py-2 pr-4 text-slate-500 text-xs max-w-md truncate">{l.details ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
