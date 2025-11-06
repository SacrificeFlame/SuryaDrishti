'use client';

interface PerformanceMetricsProps {
  metrics: {
    dieselSavings: number;
    forecastAccuracy: number;
    uptime: number;
    co2Avoided: number;
  };
}

export default function PerformanceMetrics({ metrics }: PerformanceMetricsProps) {
  const metricCards = [
    {
      label: 'Diesel Savings Today',
      value: `₹${metrics.dieselSavings.toFixed(1)}`,
      subtext: 'Liters',
      icon: '⛽',
      color: 'bg-green-50 text-green-600',
      trend: '+12%'
    },
    {
      label: 'Forecast Accuracy',
      value: `${metrics.forecastAccuracy}%`,
      subtext: 'Last 7 days',
      icon: '🎯',
      color: 'bg-blue-50 text-blue-600',
      trend: '+3%'
    },
    {
      label: 'System Uptime',
      value: `${metrics.uptime.toFixed(1)}%`,
      subtext: 'This month',
      icon: '⚡',
      color: 'bg-purple-50 text-purple-600',
      trend: '↑'
    },
    {
      label: 'CO₂ Avoided',
      value: `${metrics.co2Avoided.toFixed(1)}`,
      subtext: 'kg today',
      icon: '🌱',
      color: 'bg-emerald-50 text-emerald-600',
      trend: '+15%'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metricCards.map((metric, index) => (
        <div key={index} className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-start justify-between mb-2">
            <span className="text-3xl">{metric.icon}</span>
            <span className="text-xs font-semibold text-green-600 bg-green-100 px-2 py-1 rounded">
              {metric.trend}
            </span>
          </div>
          <div className="text-sm text-gray-600 mb-1">{metric.label}</div>
          <div className={`text-3xl font-bold mb-1 ${metric.color.split(' ')[1]}`}>
            {metric.value}
          </div>
          <div className="text-xs text-gray-500">{metric.subtext}</div>
        </div>
      ))}
    </div>
  );
}

