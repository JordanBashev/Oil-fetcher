import { Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/AppLayout";
import { RequireAdmin } from "@/components/RequireAdmin";
import { RequireAuth } from "@/components/RequireAuth";
import { AdminLogsPage } from "@/routes/AdminLogsPage";
import { AdminUsersPage } from "@/routes/AdminUsersPage";
import { DashboardPage } from "@/routes/DashboardPage";
import { ForecastListPage } from "@/routes/ForecastListPage";
import { HomePage } from "@/routes/HomePage";
import { NewForecastPage } from "@/routes/NewForecastPage";
import { ProfilePage } from "@/routes/ProfilePage";

function ProtectedShell({ children }: { children: React.ReactNode }) {
  return (
    <RequireAuth>
      <AppLayout>{children}</AppLayout>
    </RequireAuth>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route
        path="/dashboard"
        element={<ProtectedShell><DashboardPage /></ProtectedShell>}
      />
      <Route
        path="/forecasts"
        element={<ProtectedShell><ForecastListPage /></ProtectedShell>}
      />
      <Route
        path="/forecasts/new"
        element={<ProtectedShell><NewForecastPage /></ProtectedShell>}
      />
      <Route
        path="/profile"
        element={<ProtectedShell><ProfilePage /></ProtectedShell>}
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedShell>
            <RequireAdmin><AdminUsersPage /></RequireAdmin>
          </ProtectedShell>
        }
      />
      <Route
        path="/admin/logs"
        element={
          <ProtectedShell>
            <RequireAdmin><AdminLogsPage /></RequireAdmin>
          </ProtectedShell>
        }
      />
    </Routes>
  );
}
