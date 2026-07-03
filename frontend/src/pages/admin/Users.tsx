import React, { useEffect, useState } from "react";
import client from "../../api/client";

const ROLES = ["admin", "soc_lead", "analyst", "viewer"];

export default function Users() {
  const [users, setUsers] = useState<any[]>([]);
  const [form, setForm] = useState({ email: "", full_name: "", role: "analyst", password: "" });
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    const resp = await client.get("/users");
    setUsers(resp.data);
  };

  useEffect(() => {
    load();
  }, []);

  const createUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await client.post("/users", form);
      setForm({ email: "", full_name: "", role: "analyst", password: "" });
      load();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Failed to create user");
    }
  };

  const updateRole = async (id: string, role: string) => {
    await client.patch(`/users/${id}`, { role });
    load();
  };

  const toggleActive = async (id: string, is_active: boolean) => {
    await client.patch(`/users/${id}`, { is_active: !is_active });
    load();
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-xl font-semibold text-white">User & Role Management</h1>
        <p className="text-sm text-slate-400">Admin-only. Manage analyst, SOC lead, and viewer accounts.</p>
      </div>

      <div className="card">
        <h2 className="text-sm font-medium text-slate-300 mb-3">Create user</h2>
        <form onSubmit={createUser} className="grid grid-cols-2 gap-3">
          <input
            placeholder="Full name"
            value={form.full_name}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            required
          />
          <input
            placeholder="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            required
          />
          <select
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
          >
            {ROLES.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
          <input
            placeholder="Temporary password"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            required
          />
          <button className="col-span-2 bg-telnora-accent text-slate-900 font-medium rounded-lg py-2 text-sm hover:opacity-90">
            Create user
          </button>
          {error && <div className="col-span-2 text-xs text-red-400">{error}</div>}
        </form>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-800">
              <th className="py-2 pr-4">Name</th>
              <th className="py-2 pr-4">Email</th>
              <th className="py-2 pr-4">Role</th>
              <th className="py-2 pr-4">Active</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-slate-800/60">
                <td className="py-2 pr-4 text-slate-200">{u.full_name}</td>
                <td className="py-2 pr-4 text-slate-400">{u.email}</td>
                <td className="py-2 pr-4">
                  <select
                    value={u.role}
                    onChange={(e) => updateRole(u.id, e.target.value)}
                    className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs text-white"
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </td>
                <td className="py-2 pr-4">
                  <button
                    onClick={() => toggleActive(u.id, u.is_active)}
                    className={`text-xs px-2 py-1 rounded-lg border ${
                      u.is_active
                        ? "border-emerald-600 text-emerald-400"
                        : "border-slate-700 text-slate-500"
                    }`}
                  >
                    {u.is_active ? "Active" : "Disabled"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
