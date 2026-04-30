import { brand } from '../brand';
import BrandMark from './BrandMark';

export default function Footer() {
  return (
    <footer className="bg-[#322B2B] px-6 py-12 text-white lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <BrandMark tone="dark" />
          <p className="mt-4 max-w-xl text-sm leading-6 text-[#FFE7D6]">
            {brand.tagline} {brand.signature}.
          </p>
        </div>
        <div className="flex flex-wrap gap-3 text-sm font-semibold text-[#FFE7D6]">
          <a
            href="https://github.com/DevashreePawar"
            target="_blank"
            rel="noreferrer"
            className="rounded-full border border-white/10 px-4 py-2 transition hover:bg-white/10 hover:text-white"
          >
            GitHub
          </a>
          <a
            href="https://www.linkedin.com/in/devashreepawar/"
            target="_blank"
            rel="noreferrer"
            className="rounded-full border border-white/10 px-4 py-2 transition hover:bg-white/10 hover:text-white"
          >
            LinkedIn
          </a>
        </div>
      </div>
    </footer>
  );
}
