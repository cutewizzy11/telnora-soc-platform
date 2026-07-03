import React from "react";
import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import Incidents from "./pages/Incidents";
import IncidentDetail from "./pages/IncidentDetail";
import ThreatIntel from "./pages/ThreatIntel";
import Analytics from "./pages/Analytics";
import AuditLog from "./pages/AuditLog";
import About from "./pages/About";
import Users from "./pages/admin/Users";

function Protected({ children, roles }: { children: React.ReactNode; roles?: any[] }) {
  return (
    <ProtectedRoute roles={roles}>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected><Dashboard /></Protected>} />
      <Route path="/alerts" element={<Protected><Alerts /></Protected>} />
      <Route path="/incidents" element={<Protected><Incidents /></Protected>} />
      <Route path="/incidents/:id" element={<Protected><IncidentDetail /></Protected>} />
      <Route path="/threat-intel" element={<Protected><ThreatIntel /></Protected>} />
      <Route path="/analytics" element={<Protected><Analytics /></Protected>} />
      <Route
        path="/audit-log"
        element={
          <Protected roles={["admin", "soc_lead"]}>
            <AuditLog />
          </Protected>
        }
      />
      <Route
        path="/admin/users"
        element={
          <Protected roles={["admin"]}>
            <Users />
          </Protected>
        }
      />
      <Route path="/about" element={<Protected><About /></Protected>} />
    </Routes>
  );
}
