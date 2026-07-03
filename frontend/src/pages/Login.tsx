import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@telnora.io");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      navigate("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Login failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="card w-full max-w-sm">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-telnora-accent to-telnora-accent2 flex items-center justify-center font-bold text-slate-900">
            T
          </div>
          <div>
            <div className="font-semibold text-white">Telnora SOC Platform</div>
            <div className="text-xs text-slate-500">Sign in to continue</div>
          </div>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="text-xs text-slate-400">Email</label>
            <input
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-telnora-accent"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              required
            />
          </div>
          <div>
            <label className="text-xs text-slate-400">Password</label>
            <input
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-telnora-accent"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
            />
          </div>

          {error && <div className="text-xs text-red-400">{error}</div>}

          <button
            disabled={busy}
            className="w-full bg-telnora-accent text-slate-900 font-medium rounded-lg py-2 text-sm hover:opacity-90 disabled:opacity-50"
          >
            {busy ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="mt-4 text-[11px] text-slate-500 leading-relaxed">
          Demo accounts (after running the seed script):
          <br />
          admin@telnora.io / lead@telnora.io / analyst@telnora.io / viewer@telnora.io
          <br />
          password: ChangeMe123!
        </div>
      </div>
    </div>
  );
}
