import { Brain, CheckCircle2 } from 'lucide-react';

export default function AgentReasoningPanel({ reasoning = [], recommendation }) {
  const steps = reasoning?.length ? reasoning : recommendation?.reasoning_steps || [];
  if (!steps.length) return null;

  return (
    <div className="rounded-2xl border border-[#C7B7FF]/40 bg-[#FBF0FF]/80 p-4">
      <div className="flex items-center gap-2 text-sm font-bold text-[#6B4A8B]">
        <Brain className="h-4 w-4" />
        Why this view
      </div>
      <div className="mt-3 grid gap-2">
        {steps.slice(0, 4).map((step) => (
          <div key={step} className="flex gap-2 text-sm leading-6 text-[#5D4A44]">
            <CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-[#F9735B]" />
            <span>{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
