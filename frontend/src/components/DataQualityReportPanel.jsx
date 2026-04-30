import { AlertTriangle, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function DataQualityReportPanel({ report }) {
  if (!report) return null;

  const scoreTone =
    report.score >= 80
      ? 'text-[#3F7A5A] bg-[#EEF8EF]'
      : report.score >= 60
      ? 'text-[#8B672F] bg-[#FFF4D9]'
      : 'text-[#A54747] bg-[#FFF0F0]';

  return (
    <section className="pastel-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#B96B55]">Data quality</p>
          <h2 className="mt-2 text-2xl font-black text-[#322B2B]">Can we trust this dataset?</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-[#7A6F6A]">
            A quick health check before interpreting charts, averages, or rankings.
          </p>
        </div>
        <div className={`rounded-3xl px-5 py-4 text-center ${scoreTone}`}>
          <p className="text-3xl font-black">{report.score}</p>
          <p className="text-xs font-black uppercase tracking-[0.16em]">quality score</p>
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        <Metric label="Duplicate rows" value={report.duplicate_rows || 0} sub={`${report.duplicate_percentage || 0}%`} />
        <Metric label="High-missing fields" value={report.high_missing_columns?.length || 0} />
        <Metric label="Outlier fields" value={report.numeric_outliers?.length || 0} />
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <QualityList title="Needs attention" items={attentionItems(report)} icon={<AlertTriangle className="h-4 w-4" />} />
        <QualityList title="Recommendations" items={report.recommendations || []} icon={<ShieldCheck className="h-4 w-4" />} />
      </div>
    </section>
  );
}

function attentionItems(report) {
  const items = [];
  report.high_missing_columns?.slice(0, 3).forEach((item) => {
    items.push(`${item.column} has ${item.missing_percentage}% missing values.`);
  });
  report.numeric_outliers?.slice(0, 3).forEach((item) => {
    items.push(`${item.column} has ${item.count} possible outliers.`);
  });
  if (report.duplicate_rows) items.push(`${report.duplicate_rows} duplicate rows were found.`);
  if (report.likely_identifier_columns?.length) {
    items.push(`Likely identifier columns: ${report.likely_identifier_columns.slice(0, 4).join(', ')}.`);
  }
  if (Object.keys(report.sensitive_columns || {}).length) {
    items.push(`Sensitive fields detected: ${Object.keys(report.sensitive_columns).slice(0, 4).join(', ')}.`);
  }
  if (report.constant_columns?.length) {
    items.push(`Constant columns add little analytical value: ${report.constant_columns.slice(0, 4).join(', ')}.`);
  }
  if (!items.length) items.push('No major quality concerns were detected.');
  return items;
}

function QualityList({ title, items, icon }) {
  return (
    <div className="rounded-3xl border border-[#F3D8C8] bg-[#FFF8F1] p-5">
      <div className="flex items-center gap-2 text-sm font-black uppercase tracking-[0.16em] text-[#8B5E4A]">
        {icon}
        {title}
      </div>
      <div className="mt-4 space-y-3">
        {items.map((item) => (
          <p key={item} className="flex gap-2 text-sm font-semibold leading-6 text-[#5D4A44]">
            <CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-[#D9654F]" />
            {item}
          </p>
        ))}
      </div>
    </div>
  );
}

function Metric({ label, value, sub }) {
  return (
    <div className="rounded-2xl bg-[#FFF8F1] p-4">
      <p className="text-2xl font-black text-[#322B2B]">
        {value}
        {sub ? <span className="ml-2 text-sm font-bold text-[#9C6B55]">{sub}</span> : null}
      </p>
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#9C6B55]">{label}</p>
    </div>
  );
}
