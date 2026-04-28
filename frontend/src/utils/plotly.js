export function parseFigure(chartConfig) {
  if (!chartConfig) return { data: [], layout: {} };
  if (typeof chartConfig === 'string') return JSON.parse(chartConfig);
  return chartConfig;
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
