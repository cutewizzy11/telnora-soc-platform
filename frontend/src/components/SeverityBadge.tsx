import React from "react";

const LABELS: Record<string, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  info: "Info",
};

export default function SeverityBadge({ severity }: { severity: string }) {
  return (
    <span className={`severity-${severity} text-xs font-medium px-2 py-0.5 rounded-full whitespace-nowrap`}>
      {LABELS[severity] ?? severity}
    </span>
  );
}
