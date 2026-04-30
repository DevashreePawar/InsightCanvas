import { Download, FileJson, FileText, Printer } from 'lucide-react';
import { buildDashboardExport, buildDashboardHtml, slugify } from '../utils/export';
import { downloadBlob } from '../utils/plotly';

export default function ExportPanel({ dataset, question, result }) {
  if (!result) return null;

  const filename = slugify(question || result.question || 'insightcanvas-analysis');

  const downloadJson = () => {
    const payload = buildDashboardExport({ dataset, question, result });
    downloadBlob(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }), `${filename}.json`);
  };

  const downloadHtml = () => {
    const html = buildDashboardHtml({ dataset, question, result });
    downloadBlob(new Blob([html], { type: 'text/html' }), `${filename}.html`);
  };

  return (
    <section className="pastel-card p-6 print:hidden">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#B96B55]">Export</p>
          <h2 className="mt-2 text-2xl font-black text-[#322B2B]">Take this analysis with you</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-[#7A6F6A]">
            Keep a polished copy of this first read: the dashboard, the underlying analysis, or a PDF-style printout.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button type="button" onClick={downloadHtml} className="pastel-button">
            <FileText className="h-4 w-4" />
            HTML report
          </button>
          <button
            type="button"
            onClick={downloadJson}
            className="inline-flex items-center gap-2 rounded-2xl bg-[#FFF1E6] px-5 py-3 font-bold text-[#6B4A35] transition hover:-translate-y-0.5 hover:bg-[#FFE4D2]"
          >
            <FileJson className="h-4 w-4" />
            JSON data
          </button>
          <button
            type="button"
            onClick={() => window.print()}
            className="inline-flex items-center gap-2 rounded-2xl bg-[#322B2B] px-5 py-3 font-bold text-white transition hover:-translate-y-0.5 hover:bg-[#4A3B37]"
          >
            <Printer className="h-4 w-4" />
            Print / PDF
          </button>
        </div>
      </div>
      <p className="mt-4 flex items-center gap-2 rounded-2xl bg-[#FFF8F1] p-3 text-xs font-semibold leading-5 text-[#7A6F6A]">
        <Download className="h-4 w-4 shrink-0 text-[#B96B55]" />
        Individual charts can also be downloaded from each chart card.
      </p>
    </section>
  );
}
