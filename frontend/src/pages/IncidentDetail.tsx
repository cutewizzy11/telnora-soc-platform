import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import client from "../api/client";
import SeverityBadge from "../components/SeverityBadge";

const STATUS_OPTIONS = ["open", "in_progress", "contained", "resolved", "closed"];

export default function IncidentDetail() {
  const { id } = useParams();
  const [incident, setIncident] = useState<any>(null);
  const [comment, setComment] = useState("");

  const load = async () => {
    const resp = await client.get(`/incidents/${id}`);
    setIncident(resp.data);
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (!incident) return <div className="text-sm text-slate-400">Loading...</div>;

  const updateStatus = async (status: string) => {
    await client.patch(`/incidents/${id}`, { status });
    load();
  };

  const submitComment = async () => {
    if (!comment.trim()) return;
    await client.post(`/incidents/${id}/comments`, { body: comment });
    setComment("");
    load();
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-semibold text-white">{incident.title}</h1>
          <SeverityBadge severity={incident.severity} />
        </div>
        <p className="text-sm text-slate-400 mt-1">{incident.summary}</p>
      </div>

      <div className="card">
        <label className="text-xs text-slate-400">Status</label>
        <select
          value={incident.status}
          onChange={(e) => updateStatus(e.target.value)}
          className="mt-1 block bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <div className="card">
        <h2 className="text-sm font-medium text-slate-300 mb-3">Timeline / Comments</h2>
        <div className="space-y-3 mb-4">
          {incident.comments.map((c: any) => (
            <div key={c.id} className="bg-slate-900 border border-slate-800 rounded-lg p-3">
              <div className="text-xs text-slate-500 mb-1">
                {c.author_name ?? "Unknown"} · {new Date(c.created_at).toLocaleString()}
              </div>
              <div className="text-sm text-slate-200">{c.body}</div>
            </div>
          ))}
          {incident.comments.length === 0 && (
            <div className="text-xs text-slate-600">No comments yet.</div>
          )}
        </div>
        <div className="flex gap-2">
          <input
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add an update..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-telnora-accent"
          />
          <button
            onClick={submitComment}
            className="text-xs px-4 py-2 rounded-lg bg-telnora-accent text-slate-900 font-medium hover:opacity-90"
          >
            Post
          </button>
        </div>
      </div>
    </div>
  );
}
