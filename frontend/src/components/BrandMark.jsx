import { brand } from '../brand';

export default function BrandMark({ size = 'md', showText = true, tone = 'light' }) {
  const markSize = size === 'lg' ? 'h-14 w-14 rounded-[1.35rem]' : 'h-10 w-10 rounded-2xl';
  const barClass = size === 'lg' ? 'w-1.5 rounded-full' : 'w-1 rounded-full';
  const textTone = tone === 'dark' ? 'text-white' : 'text-[#322B2B]';
  const subTone = tone === 'dark' ? 'text-[#FFE7D6]' : 'text-[#8A7A72]';

  return (
    <span className="inline-flex items-center gap-3">
      <span className={`relative grid ${markSize} place-items-center bg-[#F3C7B8] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.58)]`}>
        <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-[#D9654F]" />
        <span className="flex h-6 items-end gap-1">
          <span className={`${barClass} h-3 bg-[#8B5E4A]`} />
          <span className={`${barClass} h-5 bg-[#D9654F]`} />
          <span className={`${barClass} h-4 bg-[#6B4A8B]`} />
        </span>
      </span>
      {showText ? (
        <span className="leading-tight">
          <span className={`block font-black tracking-tight ${textTone}`}>{brand.name}</span>
          {size === 'lg' ? <span className={`block text-sm font-semibold ${subTone}`}>{brand.tagline}</span> : null}
        </span>
      ) : null}
    </span>
  );
}
