'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Zap, TrendingUp, ArrowRight, X } from 'lucide-react';
import { getSystemStatus, getConfiguration, type SystemConfiguration } from '@/lib/api-client';

interface GridExportRecommendationsProps {
  microgridId: string;
}

interface Recommendation {
  id: string;
  title: string;
  message: string;
  potentialRevenue: number;
  excessEnergy: number;
  priority: 'high' | 'medium' | 'low';
}

export default function GridExportRecommendations({ microgridId }: GridExportRecommendationsProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  const [config, setConfig] = useState<SystemConfiguration | null>(null);

  useEffect(() => {
    async function loadRecommendations() {
      try {
        setLoading(true);
        
        // Get system status and configuration
        const [statusResponse, configResponse] = await Promise.allSettled([
          getSystemStatus(microgridId),
          getConfiguration(microgridId),
        ]);

        const status = statusResponse.status === 'fulfilled' ? statusResponse.value : null;
        const configuration = configResponse.status === 'fulfilled' ? configResponse.value : null;
        
        setConfig(configuration);

        if (!status || !configuration) {
          setLoading(false);
          return;
        }

        const newRecommendations: Recommendation[] = [];

        // Calculate excess energy
        const solarGeneration = status.solar_generation_kw || 0;
        const load = (status.loads?.critical || 0) + (status.loads?.nonCritical || 0);
        const batterySOC = status.battery?.soc || 0;
        const excessEnergy = Math.max(0, solarGeneration - load);

        // Check if grid export is enabled
        const isExportEnabled = configuration.grid_export_enabled;
        const exportRate = configuration.grid_export_rate_per_kwh || 0;

        // Recommendation 1: Enable grid export if disabled and there's excess energy
        if (!isExportEnabled && excessEnergy > 1.0) {
          const dailyRevenue = excessEnergy * exportRate * 8; // Assume 8 hours of excess per day
          newRecommendations.push({
            id: 'enable-export',
            title: 'Enable Grid Export',
            message: `You have ${excessEnergy.toFixed(1)} kW of excess energy. Enable grid export to earn ₹${dailyRevenue.toFixed(0)} per day.`,
            potentialRevenue: dailyRevenue,
            excessEnergy: excessEnergy,
            priority: 'high',
          });
        }

        // Recommendation 2: High excess energy during peak generation
        if (isExportEnabled && excessEnergy > 5.0 && batterySOC > 0.8) {
          const dailyRevenue = excessEnergy * exportRate * 6; // Assume 6 hours of high excess
          newRecommendations.push({
            id: 'high-excess',
            title: 'High Excess Energy Available',
            message: `You're generating ${excessEnergy.toFixed(1)} kW more than needed. Battery is full (${batterySOC.toFixed(0)}%). Export to grid to earn ₹${dailyRevenue.toFixed(0)} per day.`,
            potentialRevenue: dailyRevenue,
            excessEnergy: excessEnergy,
            priority: 'high',
          });
        }

        // Recommendation 3: Battery full and excess energy
        if (isExportEnabled && batterySOC >= 0.9 && excessEnergy > 2.0) {
          const dailyRevenue = excessEnergy * exportRate * 4; // Assume 4 hours
          newRecommendations.push({
            id: 'battery-full',
            title: 'Battery Full - Export Excess',
            message: `Battery is at ${batterySOC.toFixed(0)}% and you have ${excessEnergy.toFixed(1)} kW excess. Start exporting to maximize revenue.`,
            potentialRevenue: dailyRevenue,
            excessEnergy: excessEnergy,
            priority: 'medium',
          });
        }

        // Recommendation 4: Low export rate - suggest better provider
        if (isExportEnabled && exportRate < 3.5 && excessEnergy > 1.0) {
          const betterRate = 4.0; // Example better rate
          const additionalRevenue = excessEnergy * (betterRate - exportRate) * 6;
          newRecommendations.push({
            id: 'better-rate',
            title: 'Better Export Rate Available',
            message: `Current rate: ₹${exportRate.toFixed(2)}/kWh. Switch to a provider offering ₹${betterRate.toFixed(2)}/kWh to earn ₹${additionalRevenue.toFixed(0)} more per day.`,
            potentialRevenue: additionalRevenue,
            excessEnergy: excessEnergy,
            priority: 'medium',
          });
        }

        // Recommendation 5: No excess but export enabled
        if (isExportEnabled && excessEnergy < 0.5) {
          newRecommendations.push({
            id: 'no-excess',
            title: 'Low Excess Energy',
            message: 'Currently no excess energy to export. Monitor during peak solar hours for export opportunities.',
            potentialRevenue: 0,
            excessEnergy: excessEnergy,
            priority: 'low',
          });
        }

        // Sort by priority and revenue
        newRecommendations.sort((a, b) => {
          const priorityOrder = { high: 3, medium: 2, low: 1 };
          if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
            return priorityOrder[b.priority] - priorityOrder[a.priority];
          }
          return b.potentialRevenue - a.potentialRevenue;
        });

        setRecommendations(newRecommendations);
      } catch (err) {
        console.error('Failed to load grid export recommendations:', err);
      } finally {
        setLoading(false);
      }
    }

    loadRecommendations();
    
    // Refresh every 5 minutes
    const interval = setInterval(loadRecommendations, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [microgridId]);

  const handleDismiss = (id: string) => {
    setDismissed((prev) => new Set(prev).add(id));
  };

  const visibleRecommendations = recommendations.filter((rec) => !dismissed.has(rec.id));

  if (loading) {
    return null; // Don't show loading state, just don't render
  }

  if (visibleRecommendations.length === 0) {
    return null;
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-amber-500 bg-amber-50 dark:bg-amber-900/20';
      case 'medium':
        return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20';
      case 'low':
        return 'border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50';
      default:
        return 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return '🔥';
      case 'medium':
        return '💡';
      case 'low':
        return 'ℹ️';
      default:
        return '📢';
    }
  };

  return (
    <div className="mb-6 space-y-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50 flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          Grid Export Recommendations
        </h3>
      </div>
      
      {visibleRecommendations.slice(0, 3).map((rec) => (
        <div
          key={rec.id}
          className={`border-2 rounded-lg p-4 ${getPriorityColor(rec.priority)} transition-all hover:shadow-md`}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">{getPriorityIcon(rec.priority)}</span>
                <h4 className="font-semibold text-slate-900 dark:text-slate-50">{rec.title}</h4>
                {rec.priority === 'high' && (
                  <span className="px-2 py-0.5 text-xs font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded-full">
                    High Priority
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-700 dark:text-slate-300 mb-3">{rec.message}</p>
              {rec.potentialRevenue > 0 && (
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold">
                    <TrendingUp className="w-4 h-4" />
                    Potential: ₹{rec.potentialRevenue.toFixed(0)}/day
                  </div>
                  {rec.excessEnergy > 0 && (
                    <div className="text-slate-600 dark:text-slate-400">
                      Excess: {rec.excessEnergy.toFixed(1)} kW
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="flex items-start gap-2">
              <Link
                href="/dashboard/grid-export"
                className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap"
              >
                View Options
                <ArrowRight className="w-4 h-4" />
              </Link>
              <button
                onClick={() => handleDismiss(rec.id)}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                aria-label="Dismiss recommendation"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ))}
      
      {visibleRecommendations.length > 3 && (
        <Link
          href="/dashboard/grid-export"
          className="block text-center text-sm text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 font-medium py-2"
        >
          View {visibleRecommendations.length - 3} more recommendations →
        </Link>
      )}
    </div>
  );
}

