export default function ProfilePanel({ profile }) {
  if (!profile) return null;

  return (
    <section className="pastel-card p-6">
      <h2 className="text-xl font-black text-[#322B2B]">Dataset profile</h2>
      <div className="mt-5 grid grid-cols-2 gap-3">
        <Metric label="Rows" value={profile.row_count} />
        <Metric label="Columns" value={profile.column_count} />
        <Metric label="Dates" value={profile.date_columns?.length || 0} />
        <Metric label="Fields" value={profile.column_names?.length || 0} />
      </div>
      <div className="mt-5">
        <p className="text-sm font-semibold text-slate-700">Columns</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {profile.column_names?.map((column) => (
            <span key={column} className="rounded-full bg-[#FFF1E6] px-3 py-1 text-xs font-bold text-[#8B5E4A]">
              {column}
              {profile.logical_types?.[column] ? (
                <span className="ml-1 text-[#C7836F]">· {profile.logical_types[column].replaceAll('_', ' ')}</span>
              ) : null}
            </span>
          ))}
        </div>
      </div>
      {profile.possible_id_columns?.length || profile.multi_value_columns?.length || Object.keys(profile.sensitive_columns || {}).length ? (
        <div className="mt-5 grid gap-3">
          {Object.keys(profile.sensitive_columns || {}).length ? (
            <ProfileNote
              label="Sensitive columns redacted"
              values={Object.entries(profile.sensitive_columns).map(([column, type]) => `${column} (${type})`)}
              tone="rose"
            />
          ) : null}
          {profile.possible_id_columns?.length ? (
            <ProfileNote label="Likely IDs" values={profile.possible_id_columns} tone="amber" />
          ) : null}
          {profile.multi_value_columns?.length ? (
            <ProfileNote label="Multi-value fields" values={profile.multi_value_columns} tone="purple" />
          ) : null}
        </div>
      ) : null}
      <div className="mt-5 max-h-48 overflow-auto rounded-2xl bg-[#FFF8F1] p-4 text-xs text-[#7A6F6A]">
        {Object.entries(profile.missing_value_percentage || {}).map(([column, value]) => (
          <div key={column} className="flex justify-between gap-4 border-b border-slate-200 py-2 last:border-0">
            <span>{column}</span>
            <span>{value}% missing</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function ProfileNote({ label, values, tone }) {
  const palette =
    tone === 'rose'
      ? 'border-rose-100 bg-rose-50 text-rose-800'
      : tone === 'purple'
      ? 'border-[#C7B7FF]/40 bg-[#FBF0FF] text-[#6B4A8B]'
      : 'border-[#F6B85A]/40 bg-[#FFF4D9] text-[#7A542A]';
  return (
    <div className={`rounded-2xl border p-3 text-sm font-semibold ${palette}`}>
      {label}: {values.join(', ')}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-2xl bg-[#FFF8F1] p-4">
      <p className="text-2xl font-black text-[#322B2B]">{value}</p>
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#9C6B55]">{label}</p>
    </div>
  );
}
