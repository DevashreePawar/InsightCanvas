import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export default function ChartPreview({ data, recommendation }) {
  const { mode, xKey, yKey } = recommendation;

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        {mode === 'line' ? (
          <LineChart data={data} margin={{ top: 16, right: 20, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
            <XAxis dataKey={xKey} stroke="#475569" />
            <YAxis stroke="#475569" />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey={yKey} stroke="#2563eb" strokeWidth={4} dot={{ r: 5 }} />
          </LineChart>
        ) : mode === 'scatter' ? (
          <ScatterChart margin={{ top: 16, right: 20, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
            <XAxis dataKey={xKey} name={xKey} stroke="#475569" />
            <YAxis dataKey={yKey} name={yKey} stroke="#475569" />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Legend />
            <Scatter name={`${xKey} vs ${yKey}`} data={data} fill="#7c3aed" />
          </ScatterChart>
        ) : (
          <BarChart data={data} margin={{ top: 16, right: 20, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
            <XAxis dataKey={xKey} stroke="#475569" />
            <YAxis stroke="#475569" />
            <Tooltip />
            <Legend />
            <Bar dataKey={yKey} fill="#2563eb" radius={[8, 8, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
