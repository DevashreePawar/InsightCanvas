import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ChartViewer from '../components/ChartViewer';
import ProfilePanel from '../components/ProfilePanel';
import { api } from '../services/api';
import { parseFigure } from '../utils/plotly';

export default function SharedDashboardPage() {
  const { shareId } = useParams();
  const [session, setSession] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getSharedSession(shareId).then(setSession).catch((err) => setError(err.message));
  }, [shareId]);

  const result = session
    ? { chart_json: parseFigure(session.chart_config), chart_type: session.chart_type, insight: session.insight, recommendation: { intent: 'shared read-only' } }
    : null;

  return (
    <main className="min-h-screen bg-[#FFF8F1] px-6 py-8 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 rounded-3xl bg-gradient-to-br from-[#F9735B] via-[#F6B85A] to-[#C7B7FF] p-8 text-white shadow-[0_24px_70px_rgba(249,115,91,0.18)]">
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-white/85">Shared InsightCanvas dashboard</p>
          <h1 className="mt-2 text-3xl font-black">{session?.title || 'Loading analysis...'}</h1>
          {session ? <p className="mt-3 text-white/90">{session.question}</p> : null}
          {error ? <p className="mt-3 text-red-200">{error}</p> : null}
        </div>
        <div className="grid gap-6 lg:grid-cols-[0.8fr_1.4fr]">
          <ProfilePanel profile={session?.dataset_metadata} />
          <ChartViewer result={result} />
        </div>
      </div>
    </main>
  );
}
