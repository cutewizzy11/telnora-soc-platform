import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", roles: null },
  { to: "/alerts", label: "Alerts", roles: null },
  { to: "/incidents", label: "Incidents", roles: null },
  { to: "/threat-intel", label: "Threat Intel", roles: null },
  { to: "/analytics", label: "Analytics", roles: null },
  { to: "/audit-log", label: "Audit Log", roles: ["admin", "soc_lead"] },
  { to: "/admin/users", label: "Users", roles: ["admin"] },
  { to: "/about", label: "About", roles: null },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 bg-telnora-panel border-r border-slate-800 flex flex-col">
        <div className="px-5 py-5 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-telnora-accent to-telnora-accent2 flex items-center justify-center font-bold text-slate-900">
              T
            </div>
            <div>
              <div className="font-semibold text-white leading-tight">Telnora SOC</div>
              <div className="text-[11px] text-slate-500 leading-tight">Security Operations</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.filter((item) => !item.roles || hasRole(...(item.roles as any))).map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `block px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-telnora-accent/10 text-telnora-accent font-medium"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-slate-800 text-xs text-slate-500">
          Built by{" "}
          <a
            href="https://github.com/Telnora-Technologies"
            target="_blank"
            rel="noreferrer"
            className="text-telnora-accent hover:underline"
          >
            Telnora Technologies
          </a>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b border-slate-800 flex items-center justify-between px-6 bg-telnora-panel/50">
          <div className="text-sm text-slate-400">Security Operations Center</div>
          <div className="flex items-center gap-3">
            <div className="text-sm text-slate-300">
              {user?.full_name} <span className="text-slate-500">({user?.role})</span>
            </div>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800"
            >
              Sign out
            </button>
          </div>
        </header>
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
