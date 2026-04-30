import { parseFigure } from './plotly';

export function slugify(value = 'insightcanvas-export') {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
    .slice(0, 80) || 'insightcanvas-export';
}

export function buildDashboardExport({ dataset, question, result }) {
  return {
    exported_at: new Date().toISOString(),
    product: 'InsightCanvas',
    dataset: dataset?.metadata || result?.metadata || {},
    question: question || result?.question,
    mode: result?.mode,
    profile: result?.profile,
    summary: result?.summary,
    quality_report: result?.quality_report,
    statistical_summary: result?.statistical_summary,
    follow_up_questions: result?.follow_up_questions || [],
    charts: (result?.charts || []).map((chart) => ({
      ...chart,
      chart_json: chart.chart_json ? parseFigure(chart.chart_json) : null,
    })),
  };
}

export function buildDashboardHtml({ dataset, question, result }) {
  const payload = buildDashboardExport({ dataset, question, result });
  const charts = payload.charts || [];
  const safePayload = JSON.stringify(payload).replace(/</g, '\\u003c');
  const chartMarkup = charts
    .map(
      (chart, index) => `
        <section class="card">
          <p class="eyebrow">${escapeHtml(chart.chart_type || 'chart')}</p>
          <h2>${escapeHtml(chart.title || `Chart ${index + 1}`)}</h2>
          <div id="chart-${index}" class="chart"></div>
          <p>${escapeHtml(chart.explanation || '')}</p>
        </section>
      `
    )
    .join('');

  return `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${escapeHtml(payload.question || 'InsightCanvas report')}</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
      body { margin: 0; background: #fff8f1; color: #322b2b; font-family: Inter, Arial, sans-serif; }
      main { max-width: 1100px; margin: 0 auto; padding: 40px 24px; }
      .hero, .card { border: 1px solid #ebddd3; background: rgba(255, 253, 249, 0.92); border-radius: 24px; padding: 24px; margin-bottom: 18px; box-shadow: 0 18px 48px rgba(104, 74, 57, 0.08); }
      h1 { margin: 0; font-size: 36px; line-height: 1.1; }
      h2 { margin: 8px 0 12px; font-size: 22px; }
      p { color: #6f625d; line-height: 1.6; }
      .eyebrow { color: #b96b55; font-size: 12px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
      .metric { background: #fff8f1; border-radius: 18px; padding: 16px; font-weight: 800; }
      .chart { min-height: 420px; }
      @media print { body { background: #fff; } .card, .hero { box-shadow: none; break-inside: avoid; } }
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <p class="eyebrow">InsightCanvas export</p>
        <h1>${escapeHtml(payload.question || 'Analysis report')}</h1>
        <p>${escapeHtml(payload.summary?.title || 'Dataset analysis')}</p>
      </section>
      <section class="card">
        <h2>Dataset Summary</h2>
        <div class="grid">
          <div class="metric">Rows: ${payload.profile?.row_count ?? 'n/a'}</div>
          <div class="metric">Columns: ${payload.profile?.column_count ?? 'n/a'}</div>
          <div class="metric">Mode: ${escapeHtml(payload.mode || 'n/a')}</div>
          <div class="metric">Quality score: ${payload.quality_report?.score ?? 'n/a'}</div>
        </div>
      </section>
      <section class="card">
        <h2>Key Insights</h2>
        ${(payload.summary?.key_insights || []).map((item) => `<p>${escapeHtml(item)}</p>`).join('') || '<p>No insight summary available.</p>'}
      </section>
      <section class="card">
        <h2>Statistical Takeaways</h2>
        ${(payload.statistical_summary?.takeaways || []).map((item) => `<p>${escapeHtml(item)}</p>`).join('') || '<p>No statistical summary available.</p>'}
      </section>
      ${chartMarkup}
    </main>
    <script>
      const payload = ${safePayload};
      payload.charts.forEach((chart, index) => {
        if (!chart.chart_json) return;
        Plotly.newPlot('chart-' + index, chart.chart_json.data || [], chart.chart_json.layout || {}, { responsive: true, displaylogo: false });
      });
    </script>
  </body>
</html>`;
}

function escapeHtml(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
