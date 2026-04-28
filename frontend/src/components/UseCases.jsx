import { BriefcaseBusiness, ChartNoAxesCombined, LineChart, Megaphone, Users } from 'lucide-react';
import SectionHeader from './SectionHeader';

const useCases = [
  { icon: ChartNoAxesCombined, title: 'Business dashboards', text: 'Turn executive questions into dashboard-ready visuals.' },
  { icon: LineChart, title: 'Exploratory data analysis', text: 'Quickly test which patterns are worth deeper analysis.' },
  { icon: Megaphone, title: 'Marketing analytics', text: 'Compare channels, campaigns, spend, leads, and conversion.' },
  { icon: Users, title: 'Customer behavior analysis', text: 'Surface churn, spending, retention, and segment trends.' },
  { icon: BriefcaseBusiness, title: 'Executive reporting', text: 'Translate messy data into concise leadership updates.' },
];

export default function UseCases() {
  return (
    <section className="bg-gradient-to-br from-[#FBF0FF] via-[#FFF8F1] to-[#FADADD]/70 px-6 py-20 lg:px-8">
      <SectionHeader
        eyebrow="Use cases"
        title="Made for first-pass exploration"
        description="Useful when you want to understand a dataset before deciding what deserves deeper analysis."
      />
      <div className="mx-auto grid max-w-7xl gap-5 md:grid-cols-2 lg:grid-cols-5">
        {useCases.map((item) => {
          const Icon = item.icon;
          return (
            <article key={item.title} className="rounded-3xl border border-white/70 bg-white/70 p-6 shadow-[0_18px_48px_rgba(199,183,255,0.16)] backdrop-blur transition hover:-translate-y-1 hover:bg-white/90">
              <Icon className="h-8 w-8 text-[#F9735B]" />
              <h3 className="mt-5 text-lg font-black text-[#322B2B]">{item.title}</h3>
              <p className="mt-3 text-sm leading-6 text-[#7A6F6A]">{item.text}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
