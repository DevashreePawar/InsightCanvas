import { useEffect, useState } from 'react';
import { ExternalLink, FileDown, Trash2 } from 'lucide-react';
import ChartViewer from '../components/ChartViewer';
import { api } from '../services/api';
import { downloadBlob, parseFigure } from '../utils/plotly';

export default function SavedSessionsPage() {
  const [sessions, setSessions] = useState([]);
  const [active, setActive] = useState(null);
  const [message, setMessage] = useState('');

  const load = async () => {
    const response = await api.listSessions();
    setSessions(response);
    setActive(response[0] || null);
  };

  useEffect(() => {
    load().catch((err) => setMessage(err.message));
  }, []);

  const remove = async (id) => {
    await api.deleteSession(id);
    await load();
  };

  const exportReport = async (format) => {
    if (!active) return;
    const blob = await api.exportReport({ session_id: active.id, format });
    downloadBlob(blob, `${active.title}.${format}`);
  };

  const activeResult = active
    ? { chart_json: parseFigure(active.chart_config), chart_type: active.chart_type, insight: active.insight, recommendation: { intent: 'saved analysis' } }
    : null;

  return (
    <main className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[0.85fr_1.35fr] lg:px-8">
      <section className="pastel-card p-6">
        <h1 className="text-2xl font-black text-[#322B2B]">Saved sessions</h1>
        {message ? <p className="mt-3 text-sm text-red-700">{message}</p> : null}
        <div className="mt-6 space-y-3">
          {sessions.map((session) => (
            <article key={session.id} className={`rounded-2xl border p-4 transition ${active?.id === session.id ? 'border-[#F9735B]/50 bg-[#FFF1E6]' : 'border-white/70 bg-[#FFF8F1]'}`}>
              <button onClick={() => setActive(session)} className="block text-left">
                <p className="font-bold text-[#322B2B]">{session.title}</p>
                <p className="mt-1 text-xs text-[#7A6F6A]">{new Date(session.created_at).toLocaleString()}</p>
              </button>
              <div className="mt-3 flex gap-2">
                <a href={`/share/${session.share_id}`} className="inline-flex items-center gap-1 text-xs font-bold text-[#F9735B]">
                  <ExternalLink className="h-3 w-3" />
                  Share
                </a>
                <button onClick={() => remove(session.id)} className="inline-flex items-center gap-1 text-xs font-bold text-red-700">
                  <Trash2 className="h-3 w-3" />
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>
      <section className="space-y-4">
        {active ? (
          <div className="pastel-card p-6">
            <h2 className="text-xl font-black text-[#322B2B]">{active.title}</h2>
            <p className="mt-2 text-[#7A6F6A]">{active.question}</p>
            <div className="mt-4 flex gap-3">
              <button onClick={() => exportReport('html')} className="inline-flex items-center gap-2 rounded-xl bg-[#F9735B] px-4 py-2 font-bold text-white">
                <FileDown className="h-4 w-4" />
                HTML report
              </button>
              <button onClick={() => exportReport('pdf')} className="inline-flex items-center gap-2 rounded-xl bg-[#322B2B] px-4 py-2 font-bold text-white">
                <FileDown className="h-4 w-4" />
                PDF report
              </button>
            </div>
          </div>
        ) : null}
        <ChartViewer result={activeResult} />
      </section>
    </main>
  );
}
