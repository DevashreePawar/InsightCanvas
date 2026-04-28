import Plot from 'react-plotly.js';
import { parseFigure } from '../utils/plotly';
import AgentReasoningPanel from './AgentReasoningPanel';
import DataQualityWarnings from './DataQualityWarnings';

export default function ChartViewer({ result, onSelectSuggestion }) {
  if (!result?.chart_json) {
    if (result?.insight) {
      return (
        <section className="space-y-4 rounded-3xl border border-white/70 bg-white/80 p-5 shadow-[0_24px_70px_rgba(249,115,91,0.14)] backdrop-blur">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#B96B55]">A note before charting</p>
            <h2 className="mt-1 text-2xl font-black text-[#322B2B]">No chart generated</h2>
          </div>
          <div className="rounded-2xl bg-gradient-to-r from-[#FFF1E6] to-[#FBF0FF] p-5">
            <p className="text-sm font-semibold text-[#7A6F6A]">Generated insight</p>
            <p className="mt-2 font-semibold leading-7 text-[#5D4A44]">{result.insight}</p>
          </div>
          <AgentReasoningPanel reasoning={result.reasoning} recommendation={result.recommendation} />
          <DataQualityWarnings
            warnings={result.data_quality_warnings}
            suggestions={result.suggested_alternatives}
            onSelectSuggestion={onSelectSuggestion}
          />
        </section>
      );
    }

    return (
      <div className="grid min-h-80 place-items-center rounded-3xl border border-dashed border-[#F9735B]/30 bg-white/70 text-center text-[#7A6F6A]">
        <div>
          <p className="font-bold text-[#5D4A44]">Your visualization will appear here.</p>
          <p className="mt-2 text-sm text-[#8A7A72]">I’ll summarize the pattern once your chart is ready.</p>
        </div>
      </div>
    );
  }

  const figure = parseFigure(result.chart_json);

  return (
    <section className="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-[0_24px_70px_rgba(249,115,91,0.14)] backdrop-blur">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#B96B55]">Visualization</p>
          <h2 className="text-2xl font-black text-[#322B2B]">{result.chart_type?.toUpperCase()}</h2>
        </div>
        <p className="rounded-full bg-[#FFF1E6] px-4 py-2 text-sm font-bold text-[#8B5E4A]">
          {result.recommendation?.intent || result.interpretation?.intent}
        </p>
      </div>
      <Plot
        data={figure.data}
        layout={{ ...figure.layout, autosize: true }}
        config={{ responsive: true, displaylogo: false }}
        className="h-[460px] w-full"
        useResizeHandler
        style={{ width: '100%', height: '460px' }}
      />
      <div className="mt-4 rounded-2xl bg-gradient-to-r from-[#FFF1E6] to-[#FBF0FF] p-5">
        <p className="text-sm font-semibold text-[#7A6F6A]">Generated insight</p>
        <p className="mt-2 font-semibold leading-7 text-[#5D4A44]">{result.insight}</p>
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <AgentReasoningPanel reasoning={result.reasoning} recommendation={result.recommendation} />
        <DataQualityWarnings
          warnings={result.data_quality_warnings}
          suggestions={result.suggested_alternatives}
          onSelectSuggestion={onSelectSuggestion}
        />
      </div>
    </section>
  );
}
