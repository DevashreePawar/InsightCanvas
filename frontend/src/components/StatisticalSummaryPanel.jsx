import { BarChart3, GitCompareArrows, Sigma } from 'lucide-react';

export default function StatisticalSummaryPanel({ summary }) {
  if (!summary) return null;

  return (
    <section className="pastel-card p-6">
      <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#B96B55]">Statistical EDA</p>
      <h2 className="mt-2 text-2xl font-black text-[#322B2B]">What the numbers suggest</h2>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-[#7A6F6A]">
        A dataset-agnostic scan for distributions, relationships, category balance, and grouped differences.
      </p>

      <div className="mt-5 grid gap-3">
        {summary.takeaways?.map((takeaway) => (
          <p key={takeaway} className="rounded-2xl bg-[#FFF8F1] p-4 text-sm font-semibold leading-6 text-[#5D4A44]">
            {takeaway}
          </p>
        ))}
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <StatCard
          title="Numeric distributions"
          icon={<Sigma className="h-4 w-4" />}
          empty="No suitable numeric columns found."
          items={summary.distributions?.slice(0, 4).map((item) => ({
            key: item.column,
            primary: item.column,
            secondary: `Median ${formatNumber(item.median)} · Mean ${formatNumber(item.mean)} · Skew ${formatNumber(item.skew)}`,
          }))}
        />
        <StatCard
          title="Relationships"
          icon={<GitCompareArrows className="h-4 w-4" />}
          empty="No numeric relationships found."
          items={summary.correlations?.slice(0, 4).map((item) => ({
            key: item.columns.join('-'),
            primary: item.columns.join(' + '),
            secondary: `${item.strength} ${item.direction} correlation (${formatNumber(item.correlation)})`,
          }))}
        />
        <StatCard
          title="Grouped differences"
          icon={<BarChart3 className="h-4 w-4" />}
          empty="No grouped comparison stood out."
          items={summary.group_comparisons?.slice(0, 4).map((item) => ({
            key: `${item.group_column}-${item.metric}`,
            primary: `${item.metric} by ${item.group_column}`,
            secondary: `${item.highest_group} is highest; spread ${formatNumber(item.spread)}`,
          }))}
        />
      </div>

      {summary.categorical_balance?.length ? (
        <div className="mt-4 rounded-3xl border border-[#E8D7FF] bg-[#FBF0FF] p-5">
          <h3 className="text-sm font-black uppercase tracking-[0.16em] text-[#6B4A8B]">Category balance</h3>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {summary.categorical_balance.slice(0, 4).map((item) => (
              <p key={item.column} className="rounded-2xl bg-white/70 p-4 text-sm font-semibold leading-6 text-[#5D4A44]">
                <span className="font-black text-[#322B2B]">{item.column}</span> is led by {item.top_value} ({item.top_value_share}% of non-missing rows).
              </p>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function StatCard({ title, icon, items = [], empty }) {
  return (
    <div className="rounded-3xl border border-[#F3D8C8] bg-[#FFF8F1] p-5">
      <div className="flex items-center gap-2 text-sm font-black uppercase tracking-[0.16em] text-[#8B5E4A]">
        {icon}
        {title}
      </div>
      <div className="mt-4 space-y-3">
        {items.length ? (
          items.map((item) => (
            <div key={item.key} className="rounded-2xl bg-white/70 p-4">
              <p className="font-black text-[#322B2B]">{item.primary}</p>
              <p className="mt-1 text-sm font-semibold leading-6 text-[#7A6F6A]">{item.secondary}</p>
            </div>
          ))
        ) : (
          <p className="rounded-2xl bg-white/70 p-4 text-sm font-semibold text-[#7A6F6A]">{empty}</p>
        )}
      </div>
    </div>
  );
}

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'n/a';
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
}
