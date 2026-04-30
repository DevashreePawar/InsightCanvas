import { CheckCircle2 } from 'lucide-react';
import SectionHeader from './SectionHeader';

const impactPoints = [
  'Helps turn vague curiosity into better questions',
  'Makes first-pass exploration less intimidating',
  'Turns messy files into something easier to scan',
  'Keeps the explanation close to the evidence',
];

export default function Impact() {
  return (
    <section id="about" className="bg-gradient-to-br from-[#FFF1E6] via-white to-[#FBF0FF] px-6 py-20 lg:px-8">
      <SectionHeader
        eyebrow="Project impact"
        title="Built for thoughtful exploration"
        description="InsightCanvas is less about producing charts in bulk and more about helping the next question become clearer."
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
        <div className="mt-6 flex flex-col gap-5 rounded-3xl border border-[#EBDDD3] bg-[#FFFDF9] p-5 sm:flex-row sm:items-center">
          <img
            src="/images/profile/devashree.jpg"
            alt="Devashree Pawar"
            className="h-24 w-24 rounded-3xl object-cover shadow-[0_18px_40px_rgba(104,74,57,0.16)]"
            onError={(event) => {
              event.currentTarget.style.display = 'none';
            }}
          />
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#B96B55]">Creator note</p>
            <p className="mt-2 text-lg font-black leading-7 text-[#322B2B]">
              Built by Devashree Pawar, a data analyst exploring better ways to make data easier to understand.
            </p>
            <p className="mt-2 text-sm leading-6 text-[#7A6F6A]">
              InsightCanvas reflects that goal: a calm workspace for asking clearer questions, checking data quality, and turning patterns into something people can actually use.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
