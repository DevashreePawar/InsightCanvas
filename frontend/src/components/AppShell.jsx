import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LogOut, Sparkles } from 'lucide-react';
import { authStore } from '../services/api';

export default function AppShell() {
  const navigate = useNavigate();

  const logout = () => {
    authStore.clear();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#FFF8F1]">
      <header className="sticky top-0 z-30 border-b border-white/70 bg-[#FFF8F1]/85 backdrop-blur">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
          <Link to="/dashboard" className="flex items-center gap-3 font-black text-[#322B2B]">
            <span className="grid h-10 w-10 place-items-center rounded-2xl bg-gradient-to-br from-[#F9735B] via-[#F6B85A] to-[#C7B7FF] text-white">
              <Sparkles className="h-5 w-5" />
            </span>
            InsightCanvas
          </Link>
          <div className="flex items-center gap-3 text-sm font-semibold">
            <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'text-[#F9735B]' : 'text-[#7A6F6A] hover:text-[#F9735B]')}>
              Dashboard
            </NavLink>
            <NavLink to="/sessions" className={({ isActive }) => (isActive ? 'text-[#F9735B]' : 'text-[#7A6F6A] hover:text-[#F9735B]')}>
              Saved Sessions
            </NavLink>
            <button onClick={logout} className="inline-flex items-center gap-2 rounded-xl bg-[#322B2B] px-3 py-2 text-white transition hover:bg-[#4A3B37]">
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </nav>
      </header>
      <Outlet />
    </div>
  );
}
