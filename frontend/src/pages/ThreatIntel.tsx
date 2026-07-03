import React, { useEffect, useState } from "react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

interface IOC {
  id: string;
  type: string;
  value: string;
  source: string;
  confidence: number;
  description?: string;
  severity?: string;
  cvss_score?: number;
  last_seen: string;
}

export default function ThreatIntel() {
  const { hasRole } = useAuth();
  const [iocs, setIocs] = useState<IOC[]>([]);
  const [type, setType] = useState("");
  const [q, setQ] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [refreshResult, setRefreshResult] = useState<any>(null);

  const load = async () => {
    const params: Record<string, string> = {};
    if (type) params.type = type;
    if (q) params.q = q;
    const resp = await client.get("/threat-intel/iocs", { params });
    setIocs(resp.data);
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type]);

  const refresh = async () => {
    setRefreshing(true);
    try {
      const resp = await client.post("/threat-intel/refresh");
      setRefreshResult(resp.data);
      await load();
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-white">Threat Intelligence</h1>
          <p className="text-sm text-slate-400">
            Indicators of compromise from AbuseIPDB, AlienVault OTX, and CVEs from NVD.
          </p>
        </div>
        {hasRole("admin", "soc_lead") && (
          <button
            onClick={refresh}
            disabled={refreshing}
            className="text-xs px-3 py-2 rounded-lg bg-telnora-accent text-slate-900 font-medium hover:opacity-90 disabled:opacity-50"
          >
            {refreshing ? "Refreshing..." : "Refresh feeds"}
          </button>
        )}
      </div>

      {refreshResult && (
        <div className="text-xs text-slate-400">
          Ingested — AbuseIPDB: {refreshResult.abuseipdb}, OTX: {refreshResult.otx}, NVD: {refreshResult.nvd}
          {refreshResult.abuseipdb === 0 && refreshResult.otx === 0 && refreshResult.nvd === 0 && (
            <span className="text-slate-600"> (configure API keys in your .env to enable live feeds)</span>
          )}
        </div>
      )}

      <div className="flex gap-3">
        <input
          placeholder="Search value..."
          value={q}
          onKeyDown={(e) => e.key === "Enter" && load()}
          onChange={(e) => setQ(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-telnora-accent"
        />
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
        >
          <option value="">All types</option>
          <option value="ip">IP</option>
          <option value="domain">Domain</option>
          <option value="hash">Hash</option>
          <option value="cve">CVE</option>
        </select>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-800">
              <th className="py-2 pr-4">Value</th>
              <th className="py-2 pr-4">Type</th>
              <th className="py-2 pr-4">Source</th>
              <th className="py-2 pr-4">Confidence</th>
              <th className="py-2 pr-4">CVSS</th>
              <th className="py-2 pr-4">Description</th>
            </tr>
          </thead>
          <tbody>
            {iocs.map((i) => (
              <tr key={i.id} className="border-b border-slate-800/60 hover:bg-slate-800/30">
                <td className="py-2 pr-4 font-mono text-xs text-slate-200">{i.value}</td>
                <td className="py-2 pr-4 text-slate-400 uppercase text-xs">{i.type}</td>
                <td className="py-2 pr-4 text-slate-400">{i.source}</td>
                <td className="py-2 pr-4 text-slate-400">{i.confidence.toFixed(0)}</td>
                <td className="py-2 pr-4 text-slate-400">{i.cvss_score ?? "—"}</td>
                <td className="py-2 pr-4 text-slate-500 text-xs max-w-md truncate">{i.description ?? "—"}</td>
              </tr>
            ))}
            {iocs.length === 0 && (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-500">
                  No IOCs yet — run the seed script or click "Refresh feeds" (requires API keys).
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
