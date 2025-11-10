'use client';

import { useState, useEffect } from 'react';
import { Sun, Zap } from 'lucide-react';

interface SolarPanel {
  id: number;
  power: number;
  status: 'active' | 'inactive' | 'maintenance';
  efficiency: number;
}

interface SolarPanelsVisualizationProps {
  totalPower?: number;
  panelCount?: number;
}

export default function SolarPanelsVisualization({ 
  totalPower = 0, 
  panelCount = 24 
}: SolarPanelsVisualizationProps) {
  const [panels, setPanels] = useState<SolarPanel[]>([]);

  useEffect(() => {
    // Generate panel data
    const generatedPanels: SolarPanel[] = Array.from({ length: panelCount }, (_, i) => ({
      id: i + 1,
      power: totalPower > 0 ? (totalPower / panelCount) * (0.8 + Math.random() * 0.4) : 0,
      status: totalPower > 0 
        ? (Math.random() > 0.1 ? 'active' : Math.random() > 0.5 ? 'inactive' : 'maintenance')
        : 'inactive',
      efficiency: 0.15 + Math.random() * 0.1, // 15-25% efficiency
    }));
    setPanels(generatedPanels);
  }, [totalPower, panelCount]);

  const activePanels = panels.filter(p => p.status === 'active').length;
  const totalGenerated = panels.reduce((sum, p) => sum + p.power, 0);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/20 flex items-center justify-center">
            <Sun className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50">Solar Array</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">{panelCount} panels installed</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Total Output</div>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {totalGenerated.toFixed(1)} kW
          </div>
        </div>
      </div>

      {/* Panel Grid */}
      <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3 mb-6">
        {panels.map((panel) => (
          <div
            key={panel.id}
            className={`
              aspect-square rounded-lg border-2 transition-all
              ${panel.status === 'active' 
                ? 'bg-gradient-to-br from-amber-400/20 to-orange-500/20 border-amber-400 dark:from-amber-500/30 dark:to-orange-600/30 dark:border-amber-500' 
                : panel.status === 'maintenance'
                ? 'bg-slate-200 dark:bg-slate-700 border-slate-400 dark:border-slate-600'
                : 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 opacity-50'
              }
              ${panel.status === 'active' ? 'animate-pulse' : ''}
            `}
            title={`Panel ${panel.id}: ${panel.power.toFixed(2)} kW (${(panel.efficiency * 100).toFixed(1)}% efficiency)`}
          >
            <div className="h-full flex flex-col items-center justify-center p-2">
              <Sun 
                className={`w-4 h-4 ${
                  panel.status === 'active' 
                    ? 'text-amber-600 dark:text-amber-400' 
                    : 'text-slate-400 dark:text-slate-500'
                }`} 
              />
              <div className={`text-[8px] mt-1 font-semibold ${
                panel.status === 'active' 
                  ? 'text-amber-700 dark:text-amber-300' 
                  : 'text-slate-500 dark:text-slate-400'
              }`}>
                {panel.power > 0 ? `${panel.power.toFixed(1)}kW` : 'OFF'}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-200 dark:border-slate-800">
        <div className="text-center">
          <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Active</div>
          <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
            {activePanels}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Inactive</div>
          <div className="text-lg font-bold text-slate-600 dark:text-slate-400">
            {panels.filter(p => p.status === 'inactive').length}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Maintenance</div>
          <div className="text-lg font-bold text-amber-600 dark:text-amber-400">
            {panels.filter(p => p.status === 'maintenance').length}
          </div>
        </div>
      </div>
    </div>
  );
}

