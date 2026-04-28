export default function SectionHeader({ eyebrow, title, description }) {
  return (
    <div className="mx-auto mb-10 max-w-3xl text-center">
      <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#F9735B]">{eyebrow}</p>
      <h2 className="mt-3 text-3xl font-black tracking-tight text-[#322B2B] sm:text-4xl">{title}</h2>
      {description ? <p className="mt-4 text-base leading-7 text-[#7A6F6A]">{description}</p> : null}
    </div>
  );
}
