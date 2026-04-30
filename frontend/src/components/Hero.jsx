import { ArrowRight, FileText, MessageSquareText } from 'lucide-react';
import { brand, brandPillars } from '../brand';
import BrandMark from './BrandMark';

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-[#FFF8F1] text-[#322B2B]">
      <div className="absolute inset-0 bg-[linear-gradient(180deg,#FFF8F1_0%,#FFF3EA_58%,#FBF0FF_100%)]" />
      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
        <a href="/" className="flex items-center gap-3 font-black text-[#322B2B]" aria-label="InsightCanvas home">
          <BrandMark />
        </a>
        <nav className="hidden items-center gap-7 text-sm font-bold text-[#7A6F6A] sm:flex">
          <a href="#workflow" className="transition hover:text-[#F9735B]">How it works</a>
          <a href="#prompts" className="transition hover:text-[#F9735B]">Examples</a>
          <a href="#about" className="transition hover:text-[#F9735B]">About</a>
        </nav>
      </header>
      <div className="relative mx-auto grid min-h-[82vh] max-w-7xl items-center gap-12 px-6 pb-20 pt-10 lg:grid-cols-[1fr_0.82fr] lg:px-8">
        <div className="animate-fadeUp">
          <p className="inline-flex rounded-full border border-[#E2C8B7] bg-[#FFFDF9]/80 px-4 py-2 text-sm font-bold text-[#8B5E4A] shadow-[0_12px_30px_rgba(104,74,57,0.08)]">
            {brand.tagline}
          </p>
          <h1 className="mt-5 max-w-4xl text-5xl font-black leading-[1.05] tracking-tight text-[#322B2B] sm:text-6xl lg:text-7xl">
            {brand.promise}
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-[#6F625D] sm:text-xl">
            {brand.description}
          </p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <a
              href="/dashboard"
              className="pastel-button"
            >
              Start Exploring <ArrowRight className="h-4 w-4" />
            </a>
            <a
              href="#workflow"
              className="inline-flex items-center justify-center px-2 py-3 font-bold text-[#6B4A35] underline decoration-[#E2C8B7] decoration-2 underline-offset-8 transition hover:text-[#D9654F]"
            >
              How it works
            </a>
          </div>
          <div className="mt-6 flex max-w-2xl flex-wrap gap-2">
            {brandPillars.map((pillar) => (
              <span key={pillar} className="rounded-full bg-[#FFFDF9] px-3 py-2 text-xs font-bold text-[#8A5A48] shadow-sm">
                {pillar}
              </span>
            ))}
          </div>
        </div>

        <div className="rounded-[1.75rem] border border-[#EBDDD3] bg-[#FFFDF9] p-5 shadow-[0_20px_52px_rgba(104,74,57,0.1)]">
          <div className="rounded-[1.25rem] bg-[#FFF8F1] p-5">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-[#9C6B55]">A friendly analyst workspace</p>
                <p className="mt-1 text-xl font-black text-[#322B2B]">First-read notes</p>
              </div>
              <FileText className="h-7 w-7 text-[#B96B55]" />
            </div>
            <div className="space-y-3">
              {['Schema read gently', 'Useful fields surfaced', 'Messy values noted'].map((item) => (
                <div key={item} className="flex items-center gap-3 rounded-2xl border border-[#EBDDD3] bg-[#FFFDF9] p-4">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#D9654F]" />
                  <span className="font-semibold text-[#6F625D]">{item}</span>
                </div>
              ))}
            </div>
            <div className="mt-5 rounded-2xl border border-[#E2C8B7] bg-[#FFFDF9] p-5">
              <div className="mb-4 flex items-center gap-3 text-[#8B5E4A]">
                <MessageSquareText className="h-7 w-7" />
                <span className="text-sm font-bold">Example question</span>
              </div>
              <p className="text-lg font-black leading-7 text-[#322B2B]">“Which customer group spends the most on average?”</p>
              <p className="mt-3 text-sm leading-6 text-[#7A6F6A]">
                A clear chart appears with a short note about what the pattern may mean.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
