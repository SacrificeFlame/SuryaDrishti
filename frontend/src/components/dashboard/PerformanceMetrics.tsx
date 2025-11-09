'use client';

import { Fuel, Target, Zap, Leaf } from 'lucide-react';

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
      icon: Fuel,
      iconColor: 'text-emerald-600 dark:text-emerald-400',
      valueColor: 'text-emerald-600 dark:text-emerald-400',
      trend: '+12%'
    },
    {
      label: 'Forecast Accuracy',
      value: `${metrics.forecastAccuracy}%`,
      subtext: 'Last 7 days',
      icon: Target,
      iconColor: 'text-blue-600 dark:text-blue-400',
      valueColor: 'text-blue-600 dark:text-blue-400',
      trend: '+3%'
    },
    {
      label: 'System Uptime',
      value: `${metrics.uptime.toFixed(1)}%`,
      subtext: 'This month',
      icon: Zap,
      iconColor: 'text-purple-600 dark:text-purple-400',
      valueColor: 'text-purple-600 dark:text-purple-400',
      trend: '↑'
    },
    {
      label: 'CO₂ Avoided',
      value: `${metrics.co2Avoided.toFixed(1)}`,
      subtext: 'kg today',
      icon: Leaf,
      iconColor: 'text-teal-600 dark:text-teal-400',
      valueColor: 'text-teal-600 dark:text-teal-400',
      trend: '+15%'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metricCards.map((metric, index) => {
        const IconComponent = metric.icon;
        return (
          <div 
            key={index} 
            className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 card-hover group"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
                <IconComponent className={`w-5 h-5 ${metric.iconColor} stroke-[1.5]`} />
              </div>
              <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 px-2.5 py-1 rounded-md border border-emerald-200 dark:border-emerald-800">
                {metric.trend}
              </span>
            </div>
            <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">{metric.label}</div>
            <div className={`text-3xl font-bold mb-1.5 tracking-tight ${metric.valueColor}`}>
              {metric.value}
            </div>
            <div className="text-xs text-slate-400 dark:text-slate-500 font-medium">{metric.subtext}</div>
          </div>
        );
      })}
    </div>
  );
}

