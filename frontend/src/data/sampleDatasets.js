export const sampleDatasets = {
  Sales: [
    { month: 'Jan', revenue: 42000, orders: 720, region: 'North', profit: 12000 },
    { month: 'Feb', revenue: 46000, orders: 760, region: 'South', profit: 13500 },
    { month: 'Mar', revenue: 51000, orders: 840, region: 'West', profit: 15100 },
    { month: 'Apr', revenue: 56000, orders: 900, region: 'East', profit: 16800 },
    { month: 'May', revenue: 61000, orders: 980, region: 'North', profit: 18500 },
    { month: 'Jun', revenue: 69000, orders: 1080, region: 'West', profit: 21300 },
  ],
  'Customer Churn': [
    { segment: 'Starter', churnRate: 18, retention: 82, age: 24, spending: 120 },
    { segment: 'Growth', churnRate: 12, retention: 88, age: 31, spending: 260 },
    { segment: 'Pro', churnRate: 8, retention: 92, age: 38, spending: 410 },
    { segment: 'Enterprise', churnRate: 5, retention: 95, age: 46, spending: 680 },
    { segment: 'Legacy', churnRate: 21, retention: 79, age: 52, spending: 230 },
  ],
  'Marketing Campaigns': [
    { channel: 'Email', leads: 1240, conversionRate: 7.8, spend: 9400, revenue: 42000 },
    { channel: 'Search', leads: 1680, conversionRate: 9.4, spend: 15300, revenue: 69000 },
    { channel: 'Social', leads: 1420, conversionRate: 6.9, spend: 12600, revenue: 51000 },
    { channel: 'Events', leads: 620, conversionRate: 12.5, spend: 18100, revenue: 76000 },
    { channel: 'Partners', leads: 820, conversionRate: 10.2, spend: 7800, revenue: 58000 },
  ],
};

export const questionSuggestions = [
  'Show monthly revenue trends',
  'Compare sales by region',
  'Find the relationship between age and spending',
];
