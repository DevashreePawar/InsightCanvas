import { Link, NavLink, Outlet } from 'react-router-dom';
import BrandMark from './BrandMark';

export default function AppShell() {
  return (
    <div className="min-h-screen bg-[#FFF8F1]">
      <header className="sticky top-0 z-30 border-b border-white/70 bg-[#FFF8F1]/85 backdrop-blur">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
          <Link to="/dashboard" className="flex items-center gap-3 font-black text-[#322B2B]">
            <BrandMark />
          </Link>
          <div className="flex items-center gap-3 text-sm font-semibold">
            <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'text-[#F9735B]' : 'text-[#7A6F6A] hover:text-[#F9735B]')}>
              Workspace
            </NavLink>
            <NavLink to="/sessions" className={({ isActive }) => (isActive ? 'text-[#F9735B]' : 'text-[#7A6F6A] hover:text-[#F9735B]')}>
              Saved work
            </NavLink>
          </div>
        </nav>
      </header>
      <Outlet />
    </div>
  );
}
