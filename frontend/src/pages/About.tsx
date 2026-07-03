import React from "react";

export default function About() {
  return (
    <div className="max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold text-white">About this platform</h1>
      <div className="card space-y-3 text-sm text-slate-300 leading-relaxed">
        <p>
          The Telnora SOC Platform is an open-source Security Operations Center toolkit:
          alert triage, incident case management, real threat-intelligence correlation
          (AbuseIPDB, AlienVault OTX, NVD), analytics/SLA reporting, and role-based access
          control for SOC teams of any size.
        </p>
        <p>
          It's designed to be self-hostable and free to adapt for security teams,
          MSSPs, and researchers who want a lightweight starting point instead of
          building SOC tooling from scratch.
        </p>
        <p className="text-slate-500 text-xs pt-2 border-t border-slate-800">
          Built and maintained by{" "}
          <a href="https://github.com/Telnora-Technologies" target="_blank" rel="noreferrer" className="text-telnora-accent hover:underline">
            Telnora Technologies
          </a>
          . Contributions welcome — see the repository README for setup instructions.
        </p>
      </div>
    </div>
  );
}
