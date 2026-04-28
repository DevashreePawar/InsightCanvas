import { AlertTriangle, Lightbulb } from 'lucide-react';

export default function DataQualityWarnings({ warnings = [], suggestions = [], onSelectSuggestion }) {
  if (!warnings.length && !suggestions.length) return null;

  return (
    <div className="rounded-2xl border border-[#F6B85A]/40 bg-[#FFF4D9] p-4">
      {warnings.length ? (
        <div>
          <div className="flex items-center gap-2 text-sm font-bold text-[#7A542A]">
            <AlertTriangle className="h-4 w-4" />
            Data quality notes
          </div>
          <div className="mt-2 space-y-2">
            {warnings.slice(0, 3).map((warning) => (
              <p key={warning} className="text-sm leading-6 text-[#7A542A]">
                {warning}
              </p>
            ))}
          </div>
        </div>
      ) : null}

      {suggestions.length ? (
        <div className={warnings.length ? 'mt-4' : ''}>
          <div className="flex items-center gap-2 text-sm font-bold text-[#7A542A]">
            <Lightbulb className="h-4 w-4" />
            Better questions to try
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => onSelectSuggestion?.(suggestion)}
                className="rounded-full bg-white px-3 py-2 text-left text-xs font-bold text-[#7A542A] shadow-sm transition hover:bg-[#FFE7B8]"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
