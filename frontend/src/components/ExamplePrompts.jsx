import { MessageSquareText } from 'lucide-react';
import SectionHeader from './SectionHeader';

const prompts = [
  'Show the distribution of ratings',
  'Compare survival rate by gender',
  'Which genres have the highest average rating?',
  'What factors seem related to happiness score?',
  'Create bins and compare outcomes across them',
  'Find unusual values in this dataset',
];

export default function ExamplePrompts() {
  return (
    <section id="prompts" className="bg-[#FFF8F1] px-6 py-20 lg:px-8">
      <SectionHeader
        eyebrow="Example prompts"
        title="Questions you can ask"
        description="Start with a plain question. You can always adjust it once you see the first result."
      />
      <div className="mx-auto grid max-w-6xl gap-4 md:grid-cols-2 lg:grid-cols-3">
        {prompts.map((prompt) => (
          <article
            key={prompt}
            className="group rounded-3xl border border-[#FADADD] bg-white/75 p-5 shadow-[0_18px_48px_rgba(249,115,91,0.12)] transition hover:-translate-y-1 hover:border-[#F9735B]/40 hover:bg-white"
          >
            <MessageSquareText className="h-6 w-6 text-[#F9735B]" />
            <p className="mt-4 font-bold leading-7 text-[#5D4A44]">“{prompt}”</p>
          </article>
        ))}
      </div>
    </section>
  );
}
