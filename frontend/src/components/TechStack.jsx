import SectionHeader from './SectionHeader';

const technologies = ['Works with your CSV', 'Chooses readable charts', 'Explains the pattern', 'Handles messy values', 'Flags sensitive fields', 'Saves useful sessions'];

export default function TechStack() {
  return (
    <section id="features" className="bg-[#FFF1E6] px-6 py-20 lg:px-8">
      <SectionHeader
        eyebrow="Features"
        title="A friendly workspace for practical analysis"
        description="It is designed for the ordinary questions that come up when you first open a dataset."
      />
      <div className="mx-auto grid max-w-5xl gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {technologies.map((tech) => (
          <div key={tech} className="rounded-3xl border border-white/70 bg-white/70 p-5 text-center font-bold text-[#5D4A44] shadow-[0_18px_48px_rgba(246,184,90,0.16)] transition hover:-translate-y-1">
            {tech}
          </div>
        ))}
      </div>
    </section>
  );
}
