import React, { useEffect, useState } from "react";
import client from "../api/client";
import SeverityBadge from "../components/SeverityBadge";

interface Alert {
  id: string;
  title: string;
  source: string;
  severity: string;
  status: string;
  src_ip?: string;
  dest_ip?: string;
  asset?: string;
  ioc_match?: string;
  risk_score: number;
  created_at: string;
}

const STATUS_OPTIONS = ["new", "triaged", "escalated", "false_positive", "closed"];
const PAGE_SIZE = 25;

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);

  const load = async (targetPage = page) => {
    setLoading(true);
    const params: Record<string, string | number> = {
      limit: PAGE_SIZE,
      offset: targetPage * PAGE_SIZE,
    };
    if (severityFilter) params.severity = severityFilter;
    if (statusFilter) params.status = statusFilter;
    if (q) params.q = q;
    const resp = await client.get("/alerts", { params });
    setAlerts(resp.data);
    setTotal(Number(resp.headers["x-total-count"] ?? resp.data.length));
    setPage(targetPage);
    setLoading(false);
  };

  useEffect(() => {
    load(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [severityFilter, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const updateStatus = async (id: string, status: string) => {
    await client.patch(`/alerts/${id}`, { status });
    load();
  };

  const runCorrelation = async () => {
    await client.post("/alerts/correlate");
    load();
  };

  const goToPage = (target: number) => {
    if (target < 0 || target >= totalPages) return;
    load(target);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-white">Alerts</h1>
          <p className="text-sm text-slate-400">Triage incoming security alerts and correlate against threat intel.</p>
        </div>
        <button
          onClick={runCorrelation}
          className="text-xs px-3 py-2 rounded-lg bg-telnora-accent text-slate-900 font-medium hover:opacity-90"
        >
          Re-run correlation
        </button>
      </div>

      <div className="flex gap-3 flex-wrap">
        <input
          placeholder="Search title..."
          value={q}
          onKeyDown={(e) => e.key === "Enter" && load(0)}
          onChange={(e) => setQ(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-telnora-accent"
        />
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
        >
          <option value="">All severities</option>
          {["critical", "high", "medium", "low", "info"].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <div className="card overflow-x-auto">
        {loading ? (
          <div className="text-sm text-slate-400 p-4">Loading...</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-slate-800">
                <th className="py-2 pr-4">Title</th>
                <th className="py-2 pr-4">Severity</th>
                <th className="py-2 pr-4">Source</th>
                <th className="py-2 pr-4">Src IP</th>
                <th className="py-2 pr-4">IOC Match</th>
                <th className="py-2 pr-4">Risk</th>
                <th className="py-2 pr-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr key={a.id} className="border-b border-slate-800/60 hover:bg-slate-800/30">
                  <td className="py-2 pr-4 text-slate-200">{a.title}</td>
                  <td className="py-2 pr-4"><SeverityBadge severity={a.severity} /></td>
                  <td className="py-2 pr-4 text-slate-400">{a.source}</td>
                  <td className="py-2 pr-4 text-slate-400 font-mono text-xs">{a.src_ip ?? "—"}</td>
                  <td className="py-2 pr-4 text-xs">
                    {a.ioc_match ? (
                      <span className="text-red-400">{a.ioc_match}</span>
                    ) : (
                      <span className="text-slate-600">none</span>
                    )}
                  </td>
                  <td className="py-2 pr-4 text-slate-400">{a.risk_score.toFixed(0)}</td>
                  <td className="py-2 pr-4">
                    <select
                      value={a.status}
                      onChange={(e) => updateStatus(a.id, e.target.value)}
                      className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs text-white"
                    >
                      {STATUS_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
              {alerts.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-slate-500">
                    No alerts match these filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>
          {total === 0
            ? "No alerts"
            : `Showing ${page * PAGE_SIZE + 1}-${Math.min(total, page * PAGE_SIZE + alerts.length)} of ${total}`}
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => goToPage(page - 1)}
            disabled={page === 0 || loading}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:border-telnora-accent/60"
          >
            Previous
          </button>
          <span>
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => goToPage(page + 1)}
            disabled={page + 1 >= totalPages || loading}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:border-telnora-accent/60"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
