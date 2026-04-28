import { BarChart3, Database, MessageSquareText } from 'lucide-react';
import SectionHeader from './SectionHeader';

const steps = [
  {
    icon: Database,
    title: 'Upload your dataset',
    text: 'Start with any CSV. InsightCanvas checks the columns, missing values, and useful field types.',
  },
  {
    icon: MessageSquareText,
    title: 'Ask a question',
    text: 'Type what you are curious about, like a trend, comparison, ranking, or outlier.',
  },
  {
    icon: BarChart3,
    title: 'See the pattern',
    text: 'Get a chart with a short explanation so the result is easier to interpret.',
  },
];

export default function Workflow() {
  return (
    <section id="workflow" className="bg-[#FFF8F1] px-6 py-20 lg:px-8">
      <SectionHeader
        eyebrow="How it works"
        title="Three simple steps from CSV to clarity"
        description="InsightCanvas keeps the workflow small and practical: bring your data, ask naturally, and read the pattern."
      />
      <div className="mx-auto grid max-w-6xl gap-5 md:grid-cols-3">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <article
              key={step.title}
              className="pastel-card p-6 transition hover:-translate-y-1 hover:shadow-[0_30px_80px_rgba(249,115,91,0.18)]"
            >
              <div className="mb-5 flex items-center justify-between">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-[#F9735B] to-[#C7B7FF] text-white">
                  <Icon className="h-6 w-6" />
                </div>
                <span className="text-4xl font-black text-[#FADADD]">0{index + 1}</span>
              </div>
              <h3 className="text-lg font-black text-[#322B2B]">{step.title}</h3>
              <p className="mt-3 text-sm leading-6 text-[#7A6F6A]">{step.text}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
