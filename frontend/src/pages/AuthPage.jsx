import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { api, authStore } from '../services/api';

export default function AuthPage({ mode }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: 'demo@example.com', password: 'password123' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const isSignup = mode === 'signup';

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = isSignup ? await api.signup(form) : await api.login(form);
      authStore.set(response.token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="grid min-h-screen place-items-center bg-[radial-gradient(circle_at_20%_20%,rgba(250,218,221,0.95),transparent_28%),radial-gradient(circle_at_80%_10%,rgba(199,183,255,0.58),transparent_30%),linear-gradient(135deg,#FFF8F1,#FFF1E6,#FBF0FF)] px-6 py-12">
      <form onSubmit={submit} className="w-full max-w-md rounded-[2rem] border border-white/70 bg-white/80 p-8 shadow-[0_28px_80px_rgba(249,115,91,0.18)] backdrop-blur">
        <div className="flex items-center gap-3">
          <span className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-[#F9735B] via-[#F6B85A] to-[#C7B7FF] text-white">
            <Sparkles className="h-6 w-6" />
          </span>
          <div>
            <h1 className="text-2xl font-black text-[#322B2B]">{isSignup ? 'Create account' : 'Welcome back'}</h1>
            <p className="text-sm text-[#7A6F6A]">Use a local demo account for InsightCanvas sessions.</p>
          </div>
        </div>
        <label className="mt-8 block">
          <span className="text-sm font-semibold text-[#5D4A44]">Email</span>
          <input
            type="email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            className="mt-2 w-full rounded-2xl border border-[#FADADD] bg-white/80 px-4 py-3 text-[#322B2B] outline-none focus:border-[#F9735B] focus:ring-4 focus:ring-[#FADADD]/60"
          />
        </label>
        <label className="mt-4 block">
          <span className="text-sm font-semibold text-[#5D4A44]">Password</span>
          <input
            type="password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            className="mt-2 w-full rounded-2xl border border-[#FADADD] bg-white/80 px-4 py-3 text-[#322B2B] outline-none focus:border-[#F9735B] focus:ring-4 focus:ring-[#FADADD]/60"
          />
        </label>
        {error ? <p className="mt-4 rounded-2xl bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p> : null}
        <button disabled={loading} className="pastel-button mt-6 w-full">
          {loading ? 'Working...' : isSignup ? 'Sign up' : 'Log in'}
        </button>
        <p className="mt-5 text-center text-sm text-[#7A6F6A]">
          {isSignup ? 'Already have an account?' : 'Need an account?'}{' '}
          <Link className="font-bold text-[#F9735B]" to={isSignup ? '/login' : '/signup'}>
            {isSignup ? 'Log in' : 'Sign up'}
          </Link>
        </p>
      </form>
    </main>
  );
}
