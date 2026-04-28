import { FileUp, Lightbulb, MessageSquareText } from 'lucide-react';
import { Link } from 'react-router-dom';
import SectionHeader from './SectionHeader';

export default function WorkspacePreview() {
  return (
    <section id="demo" className="bg-[#FFF8F1] px-6 py-16 lg:px-8">
      <SectionHeader
        eyebrow="Workspace"
        title="A simple place to start asking"
        description="The upload area, prompt box, and insight panel stay close together so the workflow feels like a conversation with your dataset."
      />
      <div className="mx-auto grid max-w-6xl gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="pastel-card p-6">
          <div className="rounded-3xl border border-dashed border-[#D9B8A8] bg-[#FFF8F1] p-6 text-center">
            <FileUp className="mx-auto h-8 w-8 text-[#B96B55]" />
            <p className="mt-3 font-black text-[#322B2B]">Drop your CSV here, or choose a file</p>
            <p className="mt-2 text-sm leading-6 text-[#7A6F6A]">The app will read the columns, flag sensitive fields, and suggest a few useful questions.</p>
          </div>
          <div className="mt-5 rounded-3xl border border-[#EBDDD3] bg-white p-5">
            <div className="flex items-center gap-2 text-sm font-bold text-[#8B5E4A]">
              <MessageSquareText className="h-4 w-4" />
              What would you like to understand?
            </div>
            <p className="mt-3 rounded-2xl bg-[#FFF4EA] p-4 text-sm font-semibold text-[#6B4A35]">
              Compare average spending by customer segment
            </p>
          </div>
        </div>

        <div className="pastel-card p-6">
          <div className="flex items-center gap-2 text-sm font-bold text-[#8B5E4A]">
            <Lightbulb className="h-4 w-4" />
            Insight panel
          </div>
          <div className="mt-5 h-56 rounded-3xl border border-[#EBDDD3] bg-[#FFF8F1] p-5">
            <div className="h-full rounded-2xl bg-white p-5">
              <p className="text-sm font-bold text-[#9C6B55]">Your visualization will appear here.</p>
              <div className="mt-8 flex h-24 items-end gap-3">
                {[45, 78, 58, 92, 70].map((height, index) => (
                  <span
                    key={height}
                    className="w-full rounded-t-xl bg-[#F3C7B8]"
                    style={{ height: `${height}%`, opacity: 0.72 + index * 0.05 }}
                  />
                ))}
              </div>
              <p className="mt-5 text-sm leading-6 text-[#7A6F6A]">I’ll summarize the pattern once your chart is ready.</p>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/signup" className="pastel-button">Start Exploring</Link>
            <Link to="/dashboard" className="pastel-button-secondary">Open Workspace</Link>
          </div>
        </div>
      </div>
    </section>
  );
}
