import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";

import AppsPage from "./pages/Apps";
import FleetPage from "./pages/Fleet";
import HelpPage from "./pages/Help";
import HomePage from "./pages/Home";
import RunPage from "./pages/Run";
import SettingsPage from "./pages/Settings";
import ToolsPage from "./pages/Tools";
import StatusAuditPage from "./pages/StatusAudit";
import ChatPage from "./pages/ChatPage";
import ApiDocsPage from "./pages/ApiDocs";
import Logging from "./pages/Logging";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/tools" element={<ToolsPage />} />
        <Route path="/apps" element={<AppsPage />} />
        <Route path="/help" element={<HelpPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/run" element={<RunPage />} />
        <Route path="/fleet" element={<FleetPage />} />
        <Route path="/status" element={<StatusAuditPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/api-docs" element={<ApiDocsPage />} />
        <Route path="/logs" element={<Logging />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
