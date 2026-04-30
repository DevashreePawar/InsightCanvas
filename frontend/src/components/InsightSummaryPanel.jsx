export default function InsightSummaryPanel({ summary, followUps = [], onSelectQuestion }) {
  if (!summary) return null;

  const keyInsights = summary.key_insights || [];
  const notes = summary.dataset_notes || [];

  return (
    <section className="pastel-card p-6">
      <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#B96B55]">{summary.title || 'Mini analysis report'}</p>
      <div className="mt-4 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div>
          <h2 className="text-2xl font-black text-[#322B2B]">What stands out</h2>
          <div className="mt-4 space-y-3">
            {keyInsights.length ? (
              keyInsights.map((insight) => (
                <p key={insight} className="rounded-2xl bg-[#FFF8F1] p-4 text-sm font-semibold leading-6 text-[#5D4A44]">
                  {insight}
                </p>
              ))
            ) : (
              <p className="rounded-2xl bg-[#FFF8F1] p-4 text-sm font-semibold text-[#7A6F6A]">
                I’ll summarize the pattern once the charts are ready.
              </p>
            )}
          </div>
        </div>
        <div>
          <h3 className="text-sm font-black uppercase tracking-[0.16em] text-[#8B5E4A]">You might also explore</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {followUps.map((question) => (
              <button
                key={question}
                type="button"
                onClick={() => onSelectQuestion?.(question)}
                className="rounded-full bg-[#FFF1E6] px-3 py-2 text-left text-xs font-bold text-[#8B5E4A] transition hover:bg-[#FFE4D2]"
              >
                {question}
              </button>
            ))}
          </div>
          {notes.length ? (
            <div className="mt-5 rounded-2xl bg-[#FFF4D9] p-4 text-xs font-semibold leading-5 text-[#7A542A]">
              {notes.slice(0, 2).map((note) => (
                <p key={note}>{note}</p>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
