import { useMemo, useState } from 'react';
import { BrainCircuit, FileUp, Lightbulb, UploadCloud } from 'lucide-react';
import { questionSuggestions, sampleDatasets } from '../data/sampleDatasets';
import { parseCsv, runVisualizationAgent, summarizeDataset } from '../utils/agentLogic';
import ChartPreview from './ChartPreview';
import SectionHeader from './SectionHeader';

export default function Demo() {
  const [selectedDataset, setSelectedDataset] = useState('Sales');
  const [dataset, setDataset] = useState(sampleDatasets.Sales);
  const [question, setQuestion] = useState(questionSuggestions[0]);
  const [fileName, setFileName] = useState('');

  const recommendation = useMemo(() => runVisualizationAgent(dataset, question), [dataset, question]);
  const summary = useMemo(() => summarizeDataset(dataset), [dataset]);

  const handleDatasetChange = (event) => {
    const nextDataset = event.target.value;
    setSelectedDataset(nextDataset);
    setDataset(sampleDatasets[nextDataset]);
    setFileName('');
  };

  const handleCsvUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    const parsed = parseCsv(text);
    if (parsed.length) {
      setDataset(parsed);
      setSelectedDataset('Uploaded CSV');
      setFileName(file.name);
    }
  };

  return (
    <section id="demo" className="bg-[#FFF8F1] px-6 py-20 lg:px-8">
      <SectionHeader
        eyebrow="Interactive demo"
        title="Ask a question and see what changes"
        description="Use sample data or upload a CSV. The workspace checks the fields, chooses a readable view, and explains the result in plain language."
      />

      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[0.9fr_1.35fr]">
        <div className="pastel-card p-6">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-2xl bg-[#F9735B] text-white">
              <BrainCircuit className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-xl font-black text-[#322B2B]">Workspace controls</h3>
              <p className="text-sm text-[#7A6F6A]">Dataset, question, and upload options</p>
            </div>
          </div>

          <div className="mt-7 space-y-5">
            <label className="block">
              <span className="text-sm font-semibold text-[#5D4A44]">Sample dataset</span>
              <select
                value={selectedDataset}
                onChange={handleDatasetChange}
                className="mt-2 w-full rounded-2xl border border-[#FADADD] bg-white px-4 py-3 text-[#322B2B] outline-none transition focus:border-[#F9735B] focus:ring-4 focus:ring-[#FADADD]/60"
              >
                {Object.keys(sampleDatasets).map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
                {selectedDataset === 'Uploaded CSV' ? <option value="Uploaded CSV">Uploaded CSV</option> : null}
              </select>
            </label>

            <label className="block rounded-3xl border border-dashed border-[#F9735B]/40 bg-white p-5 text-center transition hover:border-[#F9735B] hover:bg-[#FFF1E6]">
              <UploadCloud className="mx-auto h-8 w-8 text-[#F9735B]" />
              <span className="mt-3 block text-sm font-semibold text-[#5D4A44]">
                {fileName || 'Upload a CSV dataset'}
              </span>
              <span className="mt-1 block text-xs text-[#7A6F6A]">Columns in the first row, comma separated</span>
              <input type="file" accept=".csv" onChange={handleCsvUpload} className="sr-only" />
            </label>

            <label className="block">
              <span className="text-sm font-semibold text-[#5D4A44]">Ask a question</span>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                rows={4}
                className="mt-2 w-full resize-none rounded-2xl border border-[#FADADD] bg-white px-4 py-3 text-[#322B2B] outline-none transition focus:border-[#F9735B] focus:ring-4 focus:ring-[#FADADD]/60"
              />
            </label>

            <div className="flex flex-wrap gap-2">
              {questionSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setQuestion(suggestion)}
                  className="rounded-full bg-[#FFF1E6] px-3 py-2 text-xs font-bold text-[#8B5E4A] transition hover:bg-[#FFE4D2]"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="pastel-card p-6">
          <div className="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#F9735B]">Workspace output</p>
              <h3 className="mt-1 text-2xl font-black text-[#322B2B]">{recommendation.chartType}</h3>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="rounded-2xl bg-[#FFF8F1] px-3 py-2">
                <p className="text-lg font-bold text-[#322B2B]">{summary.rows}</p>
                <p className="text-xs text-[#7A6F6A]">rows</p>
              </div>
              <div className="rounded-2xl bg-[#FFF8F1] px-3 py-2">
                <p className="text-lg font-bold text-[#322B2B]">{summary.numericCount}</p>
                <p className="text-xs text-[#7A6F6A]">metrics</p>
              </div>
              <div className="rounded-2xl bg-[#FFF8F1] px-3 py-2">
                <p className="text-lg font-bold text-[#322B2B]">{summary.categoryCount}</p>
                <p className="text-xs text-[#7A6F6A]">groups</p>
              </div>
            </div>
          </div>

          <ChartPreview data={dataset} recommendation={recommendation} />

          <div className="grid gap-4 pt-4 md:grid-cols-2">
            <div className="rounded-2xl bg-[#FFF1E6] p-5">
              <div className="flex items-center gap-2 font-bold text-[#8B5E4A]">
                <FileUp className="h-5 w-5" />
                Explanation
              </div>
              <p className="mt-2 text-sm leading-6 text-[#5D4A44]">{recommendation.explanation}</p>
            </div>
            <div className="rounded-2xl bg-[#FBF0FF] p-5">
              <div className="flex items-center gap-2 font-bold text-[#6B4A8B]">
                <Lightbulb className="h-5 w-5" />
                Recommended insight
              </div>
              <p className="mt-2 text-sm leading-6 text-[#5D4A44]">{recommendation.insight}</p>
            </div>
          </div>

          <p className="mt-4 text-xs text-[#7A6F6A]">Detected fields: {summary.fields}</p>
        </div>
      </div>
    </section>
  );
}
