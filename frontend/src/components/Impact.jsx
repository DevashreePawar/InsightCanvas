import { CheckCircle2 } from 'lucide-react';
import SectionHeader from './SectionHeader';

const impactPoints = [
  'Helps you ask better questions',
  'Makes first-pass exploration less intimidating',
  'Turns messy CSVs into something easier to scan',
  'Keeps the explanation close to the chart',
];

export default function Impact() {
  return (
    <section id="about" className="bg-gradient-to-br from-[#FFF1E6] via-white to-[#FBF0FF] px-6 py-20 lg:px-8">
      <SectionHeader
        eyebrow="Project impact"
        title="Built for thoughtful exploration"
        description="InsightCanvas is less about producing charts in bulk and more about making the next question clearer."
      />
      <div className="mx-auto max-w-4xl rounded-3xl border border-white bg-white/80 p-8 shadow-[0_24px_70px_rgba(249,115,91,0.14)] backdrop-blur">
        <div className="grid gap-4 sm:grid-cols-2">
          {impactPoints.map((point) => (
            <div key={point} className="flex items-start gap-3 rounded-2xl bg-[#FFF8F1] p-5">
              <CheckCircle2 className="mt-0.5 h-5 w-5 flex-none text-[#F9735B]" />
              <p className="font-bold text-[#5D4A44]">{point}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
