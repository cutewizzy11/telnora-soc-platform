import React from "react";

export default function StatCard({
  label,
  value,
  sublabel,
}: {
  label: string;
  value: React.ReactNode;
  sublabel?: string;
}) {
  return (
    <div className="card flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-slate-400">{label}</span>
      <span className="text-2xl font-semibold text-white">{value}</span>
      {sublabel && <span className="text-xs text-slate-500">{sublabel}</span>}
    </div>
  );
}
