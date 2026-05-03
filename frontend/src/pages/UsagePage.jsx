import { useEffect, useState } from 'react';
import { BarChart3, Eye, Loader2, MousePointerClick, UploadCloud, Users } from 'lucide-react';
import { api } from '../services/api';

const metricCards = [
  { key: 'unique_visitors', label: 'Visitors', icon: Users },
  { key: 'dashboard_views', label: 'Dashboard views', icon: Eye },
  { key: 'analysis_runs', label: 'Analyses run', icon: BarChart3 },
  { key: 'uploads', label: 'Uploads', icon: UploadCloud },
];

function formatEventName(value) {
  return value.replaceAll('_', ' ');
}

export default function UsagePage() {
  const [summary, setSummary] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getAnalyticsSummary(30)
      .then(setSummary)
      .catch((err) => setMessage(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
      <section className="pastel-card p-6">
        <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#F9735B]">Usage</p>
        <h1 className="mt-2 text-3xl font-black text-[#322B2B]">Is anyone exploring InsightCanvas?</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-[#7A6F6A]">
          This page shows anonymous activity from the last 30 days, like dashboard views, uploads, and analyses. It does not store uploaded data, question text, names, emails, or file contents.
        </p>
      </section>

      {loading ? (
        <div className="mt-6 pastel-card flex items-center gap-3 p-6 text-[#7A6F6A]">
          <Loader2 className="h-5 w-5 animate-spin text-[#F9735B]" />
          Reading usage activity...
        </div>
      ) : null}

      {message ? <p className="mt-6 rounded-2xl bg-red-50 p-4 text-sm font-semibold text-red-700">{message}</p> : null}

      {summary ? (
        <>
          <section className="mt-6 grid gap-4 md:grid-cols-4">
            {metricCards.map(({ key, label, icon: Icon }) => (
              <article key={key} className="pastel-card p-5">
                <Icon className="h-5 w-5 text-[#F9735B]" />
                <p className="mt-4 text-3xl font-black text-[#322B2B]">{summary[key] || 0}</p>
                <p className="mt-1 text-sm font-bold text-[#7A6F6A]">{label}</p>
              </article>
            ))}
          </section>

          <section className="mt-6 grid gap-6 lg:grid-cols-[1fr_1fr]">
            <div className="pastel-card p-6">
              <h2 className="text-xl font-black text-[#322B2B]">Events</h2>
              <div className="mt-4 space-y-3">
                {summary.events_by_name?.length ? (
                  summary.events_by_name.map((item) => (
                    <div key={item.event_name} className="flex items-center justify-between rounded-2xl bg-[#FFF8F1] px-4 py-3">
                      <span className="inline-flex items-center gap-2 text-sm font-bold capitalize text-[#5D4A44]">
                        <MousePointerClick className="h-4 w-4 text-[#D9654F]" />
                        {formatEventName(item.event_name)}
                      </span>
                      <span className="font-black text-[#322B2B]">{item.count}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-[#7A6F6A]">No tracked activity yet.</p>
                )}
              </div>
            </div>

            <div className="pastel-card p-6">
              <h2 className="text-xl font-black text-[#322B2B]">Recent Activity</h2>
              <div className="mt-4 space-y-3">
                {summary.recent_events?.length ? (
                  summary.recent_events.slice(0, 8).map((item, index) => (
                    <article key={`${item.created_at}-${index}`} className="rounded-2xl bg-[#FFF8F1] px-4 py-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-black capitalize text-[#5D4A44]">{formatEventName(item.event_name)}</p>
                        <p className="text-xs font-semibold text-[#8A7A72]">{new Date(`${item.created_at}Z`).toLocaleString()}</p>
                      </div>
                      <p className="mt-1 text-xs font-semibold text-[#8A7A72]">{item.page || 'Unknown page'}</p>
                    </article>
                  ))
                ) : (
                  <p className="text-sm text-[#7A6F6A]">Open the dashboard once and this list will start filling in.</p>
                )}
              </div>
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}
