import { useState } from 'react';
import { FileUp, Loader2, Save, Sparkles } from 'lucide-react';
import DashboardGrid from '../components/DashboardGrid';
import DataQualityReportPanel from '../components/DataQualityReportPanel';
import ExportPanel from '../components/ExportPanel';
import InsightSummaryPanel from '../components/InsightSummaryPanel';
import ProfilePanel from '../components/ProfilePanel';
import StatisticalSummaryPanel from '../components/StatisticalSummaryPanel';
import { brand } from '../brand';
import { api } from '../services/api';
import { generateQuestionOptions } from '../utils/questionSuggestions';

const sampleOptions = [
  { label: 'Sales', value: 'sales' },
  { label: 'Customer Churn', value: 'customer-churn' },
  { label: 'Marketing Campaigns', value: 'marketing-campaigns' },
];

export default function DashboardPage() {
  const [dataset, setDataset] = useState(null);
  const [question, setQuestion] = useState('Show monthly revenue trends');
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('quick');
  const activeQuestionOptions = dataset?.suggested_questions?.length
    ? dataset.suggested_questions
    : generateQuestionOptions(dataset?.profile);

  const run = async (action) => {
    setLoading(true);
    setMessage('');
    try {
      await action();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (name) =>
    run(async () => {
      const response = await api.loadSample(name);
      setDataset(response);
      setResult(null);
      setQuestion((response.suggested_questions?.length ? response.suggested_questions : generateQuestionOptions(response.profile))[0]);
      setMessage(`Loaded ${response.metadata.filename}`);
    });

  const uploadFile = (file) =>
    run(async () => {
      const response = await api.uploadFile(file);
      setDataset(response);
      setResult(null);
      setQuestion((response.suggested_questions?.length ? response.suggested_questions : generateQuestionOptions(response.profile))[0]);
      setMessage(`Uploaded ${response.metadata.filename}`);
    });

  const analyze = (saveSession = false) =>
    run(async () => {
      if (!dataset?.dataset_id) throw new Error('Upload or load a dataset first.');
      const response = await api.runAnalysis({
        dataset_id: dataset.dataset_id,
        question,
        mode,
        save_session: saveSession,
        title: question,
      });
      setResult(response);
      setMessage(saveSession ? 'Analysis generated and saved.' : 'Analysis generated.');
    });

  const busyMessage = loading && !dataset ? 'Reading your dataset...' : loading ? (mode === 'dashboard' ? 'Building a small dashboard...' : 'Working through your question...') : message;

  return (
    <main className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[0.8fr_1.4fr] lg:px-8">
      <aside className="space-y-6">
        <section className="pastel-card p-6">
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#F9735B]">Workspace</p>
          <h1 className="mt-2 text-2xl font-black text-[#322B2B]">{brand.promise}</h1>
          <p className="mt-2 text-sm leading-6 text-[#7A6F6A]">
            Bring a file, ask what you are curious about, and let the workspace shape a readable first pass.
          </p>
          {dataset?.metadata ? (
            <p className="mt-3 rounded-2xl bg-[#FFF8F1] p-3 text-xs font-bold text-[#8B5E4A]">
              {dataset.metadata.file_type?.toUpperCase()} loaded
              {dataset.metadata.sheet_name ? ` · Sheet: ${dataset.metadata.sheet_name}` : ''}
            </p>
          ) : null}
          <div className="mt-6 grid gap-3">
            {sampleOptions.map((item) => (
              <button key={item.value} onClick={() => loadSample(item.value)} className="rounded-2xl bg-[#FFF1E6] px-4 py-3 text-left font-bold text-[#6B4A35] transition hover:-translate-y-0.5 hover:bg-[#FFE4D2]">
                {item.label}
              </button>
            ))}
          </div>
          <label className="mt-5 block rounded-3xl border border-dashed border-[#F9735B]/40 bg-[#FFF4EA] p-5 text-center transition hover:border-[#F9735B] hover:bg-[#FFE7D6]">
            <FileUp className="mx-auto h-8 w-8 text-[#F9735B]" />
            <span className="mt-2 block font-bold text-[#5D4A44]">Drop your data file here, or choose a file</span>
            <span className="mt-1 block text-xs font-semibold text-[#8A7A72]">CSV, Excel, or JSON. InsightCanvas will read the fields and suggest a few starting questions.</span>
            <input
              type="file"
              accept=".csv,text/csv,.xlsx,.xls,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,.json,application/json"
              className="sr-only"
              onChange={(event) => event.target.files?.[0] && uploadFile(event.target.files[0])}
            />
          </label>
        </section>
        <ProfilePanel profile={dataset?.profile || result?.profile} />
      </aside>

      <section className="space-y-6">
        <div className="pastel-card p-6">
          <div className="mb-5 inline-flex rounded-2xl border border-[#E2C8B7] bg-[#FFF8F1] p-1">
            {[
              ['quick', 'Quick Insight'],
              ['dashboard', 'Full Dashboard'],
            ].map(([value, label]) => (
              <button
                key={value}
                type="button"
                onClick={() => setMode(value)}
                className={`rounded-xl px-4 py-2 text-sm font-black transition ${
                  mode === value ? 'bg-[#D9654F] text-white shadow-sm' : 'text-[#7A6F6A] hover:text-[#D9654F]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          <label className="block">
            <span className="text-sm font-bold text-[#5D4A44]">What would you like to understand first?</span>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows={3}
              className="mt-2 w-full resize-none rounded-2xl border border-[#FADADD] bg-white/80 px-4 py-3 text-[#322B2B] outline-none focus:border-[#F9735B] focus:ring-4 focus:ring-[#FADADD]/60"
            />
          </label>
          <div className="mt-4 flex flex-wrap gap-2">
            {activeQuestionOptions.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setQuestion(option)}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  question === option
                    ? 'bg-[#F9735B] text-white shadow-lg shadow-[#FADADD]'
                    : 'bg-[#FFF1E6] text-[#8B5E4A] hover:bg-[#FFE4D2]'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <button onClick={() => analyze(false)} disabled={loading} className="pastel-button">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              {mode === 'dashboard' ? 'Build dashboard' : 'Generate insight'}
            </button>
            <button onClick={() => analyze(true)} disabled={loading} className="inline-flex items-center gap-2 rounded-2xl bg-[#322B2B] px-5 py-3 font-bold text-white transition hover:-translate-y-0.5 hover:bg-[#4A3B37] disabled:opacity-60">
              <Save className="h-4 w-4" />
              Generate + save
            </button>
          </div>
          {busyMessage ? <p className="mt-4 rounded-2xl bg-[#FFF8F1] p-3 text-sm font-semibold text-[#6B4A35]">{busyMessage}</p> : null}
        </div>
        <InsightSummaryPanel summary={result?.summary} followUps={result?.follow_up_questions} onSelectQuestion={setQuestion} />
        <ExportPanel dataset={dataset} question={question} result={result} />
        <DataQualityReportPanel report={result?.quality_report} />
        <StatisticalSummaryPanel summary={result?.statistical_summary} />
        <DashboardGrid charts={result?.charts || []} />
      </section>
    </main>
  );
}
