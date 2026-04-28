const fallbackQuestions = [
  'Summarize the strongest trend',
  'Compare the main metric by category',
  'Find the relationship between two numeric columns',
  'Show the distribution of a numeric column',
];

const prettify = (column) => column.replaceAll('_', ' ').replaceAll('-', ' ');

const isNumericType = (dtype = '') => dtype.includes('int') || dtype.includes('float') || dtype.includes('double');

export function generateQuestionOptions(profile) {
  if (!profile?.column_names?.length) return fallbackQuestions;

  const dateColumns = profile.date_columns || [];
  const numericColumns = profile.column_names.filter((column) => isNumericType(profile.data_types?.[column]));
  const categoricalColumns = profile.column_names.filter(
    (column) => !numericColumns.includes(column) && !dateColumns.includes(column),
  );
  const questions = [];

  if (dateColumns.length && numericColumns.length) {
    questions.push(`Show ${prettify(numericColumns[0])} trends over ${prettify(dateColumns[0])}`);
  }

  if (categoricalColumns.length && numericColumns.length) {
    questions.push(`Compare ${prettify(numericColumns[0])} by ${prettify(categoricalColumns[0])}`);
  }

  if (numericColumns.length >= 2) {
    questions.push(`Find the relationship between ${prettify(numericColumns[0])} and ${prettify(numericColumns[1])}`);
  }

  if (numericColumns.length) {
    questions.push(`Show the distribution of ${prettify(numericColumns[0])}`);
  }

  if (categoricalColumns.length) {
    questions.push(`Show the breakdown of records by ${prettify(categoricalColumns[0])}`);
  }

  return [...new Set(questions)].slice(0, 4).concat(fallbackQuestions).slice(0, 4);
}
