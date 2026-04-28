export default function Footer() {
  return (
    <footer className="bg-[#322B2B] px-6 py-10 text-white lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <p className="font-semibold">InsightCanvas · Built by Devashree Pawar</p>
        <div className="flex flex-wrap gap-4 text-sm text-[#FFE7D6]">
          <a href="#" className="transition hover:text-white">
            GitHub link
          </a>
          <a href="#" className="transition hover:text-white">
            LinkedIn link
          </a>
          <a href="#" className="transition hover:text-white">
            Portfolio link
          </a>
        </div>
      </div>
    </footer>
  );
}
