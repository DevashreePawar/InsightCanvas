const numericValue = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : value;
};

export const parseCsv = (text) => {
  const rows = text
    .trim()
    .split(/\r?\n/)
    .map((row) => row.split(',').map((cell) => cell.trim()));

  if (rows.length < 2) return [];

  const headers = rows[0];
  return rows.slice(1).map((row) =>
    headers.reduce((record, header, index) => {
      record[header] = numericValue(row[index]);
      return record;
    }, {}),
  );
};

const getFields = (dataset) => {
  const firstRow = dataset[0] ?? {};
  const fields = Object.keys(firstRow);
  const numeric = fields.filter((field) => dataset.some((row) => typeof row[field] === 'number'));
  const categorical = fields.filter((field) => !numeric.includes(field));
  return { fields, numeric, categorical };
};

const titleCase = (value) =>
  value.replace(/([A-Z])/g, ' $1').replace(/^./, (char) => char.toUpperCase());

export const runVisualizationAgent = (dataset, question) => {
  const normalizedQuestion = question.toLowerCase();
  const { numeric, categorical } = getFields(dataset);
  const defaultCategory = categorical[0] ?? 'category';
  const defaultMetric = numeric[0] ?? 'value';
  const secondaryMetric = numeric[1] ?? defaultMetric;

  // Mock agent reasoning: classify the user intent, then map it to the most useful chart pattern.
  if (normalizedQuestion.includes('relationship') || normalizedQuestion.includes('correlation')) {
    return {
      chartType: 'Scatter plot',
      xKey: numeric.includes('age') ? 'age' : defaultMetric,
      yKey: numeric.includes('spending') ? 'spending' : secondaryMetric,
      mode: 'scatter',
      explanation:
        'The agent detected a relationship question, so it selected a scatter plot to compare two numeric fields.',
      insight:
        'Higher-value customer groups tend to cluster at stronger spending levels, which can guide segmentation and targeting.',
    };
  }

  if (
    normalizedQuestion.includes('trend') ||
    normalizedQuestion.includes('monthly') ||
    normalizedQuestion.includes('over time')
  ) {
    return {
      chartType: 'Line chart',
      xKey: categorical.includes('month') ? 'month' : defaultCategory,
      yKey: numeric.includes('revenue') ? 'revenue' : defaultMetric,
      mode: 'line',
      explanation:
        'The agent found a time-oriented question and selected a line chart to make the trend easy to scan.',
      insight:
        'The upward movement suggests momentum is building, making this a strong candidate for forecasting or goal tracking.',
    };
  }

  // Comparisons are the fallback because they are common in business questions and work well with categories.
  return {
    chartType: 'Bar chart',
    xKey: normalizedQuestion.includes('region') && categorical.includes('region') ? 'region' : defaultCategory,
    yKey: numeric.includes('sales') ? 'sales' : numeric.includes('revenue') ? 'revenue' : defaultMetric,
    mode: 'bar',
    explanation:
      'The agent interpreted the prompt as a comparison and selected a bar chart for clear category-to-category ranking.',
    insight:
      'The highest-performing categories reveal where leaders can double down and where underperforming areas need support.',
  };
};

export const summarizeDataset = (dataset) => {
  const { fields, numeric, categorical } = getFields(dataset);
  return {
    rows: dataset.length,
    fields: fields.map(titleCase).join(', '),
    numericCount: numeric.length,
    categoryCount: categorical.length,
  };
};
