import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppShell from './components/AppShell';
import AnalyticsTracker from './components/AnalyticsTracker';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
import SavedSessionsPage from './pages/SavedSessionsPage';
import SharedDashboardPage from './pages/SharedDashboardPage';
import UsagePage from './pages/UsagePage';

export default function App() {
  return (
    <BrowserRouter>
      <AnalyticsTracker />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/share/:shareId" element={<SharedDashboardPage />} />
        <Route element={<AppShell />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/sessions" element={<SavedSessionsPage />} />
          <Route path="/usage" element={<UsagePage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
