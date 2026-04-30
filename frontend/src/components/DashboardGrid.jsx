import { useRef } from 'react';
import Plot from 'react-plotly.js';
import { FileJson, ImageDown } from 'lucide-react';
import { slugify } from '../utils/export';
import { downloadBlob, parseFigure } from '../utils/plotly';

export default function DashboardGrid({ charts = [] }) {
  const chartRefs = useRef({});

  if (!charts.length) {
    return (
      <div className="grid min-h-80 place-items-center rounded-3xl border border-dashed border-[#D9B8A8] bg-white/70 text-center text-[#7A6F6A]">
        <div>
          <p className="font-bold text-[#5D4A44]">Your dashboard will appear here.</p>
          <p className="mt-2 text-sm text-[#8A7A72]">Run a quick insight or full dashboard to see the pattern.</p>
        </div>
      </div>
    );
  }

  return (
    <section className="grid gap-5 xl:grid-cols-2">
      {charts.map((chart, index) => {
        const figure = chart.chart_json ? parseFigure(chart.chart_json) : null;
        const chartId = chart.id || `${slugify(chart.title || 'chart')}-${index}`;
        return (
          <article key={chartId} className="pastel-card overflow-hidden p-5">
            <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#B96B55]">{chart.chart_type?.replaceAll('_', ' ')}</p>
                <h3 className="mt-1 text-xl font-black text-[#322B2B]">{chart.title}</h3>
              </div>
              {figure ? (
                <div className="flex gap-2 print:hidden">
                  <button
                    type="button"
                    onClick={() => downloadChartImage(chartRefs.current[chartId], chart.title)}
                    className="rounded-xl bg-[#FFF1E6] p-2 text-[#8B5E4A] transition hover:bg-[#FFE4D2]"
                    aria-label={`Download ${chart.title} as PNG`}
                    title="Download PNG"
                  >
                    <ImageDown className="h-4 w-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => downloadChartJson(figure, chart.title)}
                    className="rounded-xl bg-[#FFF1E6] p-2 text-[#8B5E4A] transition hover:bg-[#FFE4D2]"
                    aria-label={`Download ${chart.title} data as JSON`}
                    title="Download JSON"
                  >
                    <FileJson className="h-4 w-4" />
                  </button>
                </div>
              ) : null}
            </div>
            {figure ? (
              <Plot
                data={figure.data}
                layout={{ ...figure.layout, autosize: true }}
                config={{ responsive: true, displaylogo: false }}
                useResizeHandler
                style={{ width: '100%', height: '360px' }}
                className="h-[360px] w-full"
                onInitialized={(_figure, graphDiv) => {
                  chartRefs.current[chartId] = graphDiv;
                }}
                onUpdate={(_figure, graphDiv) => {
                  chartRefs.current[chartId] = graphDiv;
                }}
              />
            ) : (
              <div className="grid h-[360px] place-items-center rounded-2xl bg-[#FFF8F1] text-center text-sm font-semibold text-[#7A6F6A]">
                {chart.explanation || 'This chart could not be generated from the selected fields.'}
              </div>
            )}
            {chart.explanation ? (
              <p className="mt-4 rounded-2xl bg-[#FFF8F1] p-4 text-sm font-semibold leading-6 text-[#5D4A44]">{chart.explanation}</p>
            ) : null}
          </article>
        );
      })}
    </section>
  );
}

function downloadChartJson(figure, title) {
  const filename = `${slugify(title || 'chart')}.json`;
  downloadBlob(new Blob([JSON.stringify(figure, null, 2)], { type: 'application/json' }), filename);
}

async function downloadChartImage(graphDiv, title) {
  if (!graphDiv || !window.Plotly?.downloadImage) return;
  await window.Plotly.downloadImage(graphDiv, {
    format: 'png',
    filename: slugify(title || 'chart'),
    width: 1200,
    height: 800,
    scale: 2,
  });
}
