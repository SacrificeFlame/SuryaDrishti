'use client';

import { useState, useEffect } from 'react';
import { Sun, Zap, RotateCw, Compass, Maximize2 } from 'lucide-react';

interface SolarPanel {
  id: number;
  power: number;
  status: 'active' | 'inactive' | 'maintenance';
  efficiency: number;
  angle: number; // Panel tilt angle in degrees
  azimuth: number; // Panel azimuth angle in degrees
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
  const [tiltAngle, setTiltAngle] = useState(30); // Default 30 degrees tilt
  const [azimuthAngle, setAzimuthAngle] = useState(180); // Default 180 degrees (south)
  const [autoAdjust, setAutoAdjust] = useState(true); // Auto-adjust based on sun position
  const [optimizationMode, setOptimizationMode] = useState<'manual' | 'auto' | 'optimal'>('optimal');

  // Calculate optimal angle based on time of day and sun position
  useEffect(() => {
    if (autoAdjust && optimizationMode === 'auto') {
      const now = new Date();
      const hour = now.getHours();
      const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 0).getTime()) / 86400000);
      
      // Calculate sun elevation (simplified)
      const latitude = 28.4595; // Rajasthan latitude
      const declination = 23.45 * Math.sin((360 * (284 + dayOfYear) / 365) * Math.PI / 180);
      const hourAngle = (hour - 12) * 15;
      const elevation = Math.asin(
        Math.sin(latitude * Math.PI / 180) * Math.sin(declination * Math.PI / 180) +
        Math.cos(latitude * Math.PI / 180) * Math.cos(declination * Math.PI / 180) * Math.cos(hourAngle * Math.PI / 180)
      ) * 180 / Math.PI;
      
      // Optimal tilt is approximately equal to latitude, adjusted for season
      const optimalTilt = Math.max(0, Math.min(90, latitude - declination + (elevation > 0 ? elevation * 0.3 : 0)));
      setTiltAngle(Math.round(optimalTilt));
      
      // Azimuth tracks sun position (180 = south, optimal for northern hemisphere)
      const optimalAzimuth = hour < 12 ? 180 - (12 - hour) * 15 : 180 + (hour - 12) * 15;
      setAzimuthAngle(Math.max(90, Math.min(270, optimalAzimuth)));
    }
  }, [autoAdjust, optimizationMode]);

  useEffect(() => {
    // Calculate power efficiency based on angle alignment with sun
    const calculatePowerMultiplier = (panelAngle: number, panelAzimuth: number) => {
      // Simplified: panels aligned with optimal angles get better efficiency
      const tiltDiff = Math.abs(panelAngle - tiltAngle) / 90;
      const azimuthDiff = Math.abs(panelAzimuth - azimuthAngle) / 180;
      const alignment = 1 - (tiltDiff * 0.3 + azimuthDiff * 0.2); // Up to 50% reduction for misalignment
      return Math.max(0.5, Math.min(1.0, alignment));
    };

    // Generate panel data with angles
    const generatedPanels: SolarPanel[] = Array.from({ length: panelCount }, (_, i) => {
      const panelAngle = tiltAngle + (Math.random() - 0.5) * 5; // Slight variation
      const panelAzimuth = azimuthAngle + (Math.random() - 0.5) * 10; // Slight variation
      const powerMultiplier = calculatePowerMultiplier(panelAngle, panelAzimuth);
      
      return {
        id: i + 1,
        power: totalPower > 0 
          ? (totalPower / panelCount) * powerMultiplier * (0.8 + Math.random() * 0.4)
          : 0,
        status: totalPower > 0 
          ? (Math.random() > 0.1 ? 'active' : Math.random() > 0.5 ? 'inactive' : 'maintenance')
          : 'inactive',
        efficiency: (0.15 + Math.random() * 0.1) * powerMultiplier,
        angle: panelAngle,
        azimuth: panelAzimuth,
      };
    });
    setPanels(generatedPanels);
  }, [totalPower, panelCount, tiltAngle, azimuthAngle]);

  const activePanels = panels.filter(p => p.status === 'active').length;
  const totalGenerated = panels.reduce((sum, p) => sum + p.power, 0);
  const averageEfficiency = panels.length > 0 
    ? (panels.reduce((sum, p) => sum + p.efficiency, 0) / panels.length) * 100 
    : 0;

  const handleOptimize = () => {
    setOptimizationMode('optimal');
    setAutoAdjust(true);
    // Calculate optimal angles for maximum sun exposure
    const now = new Date();
    const hour = now.getHours();
    // Optimal tilt for Rajasthan (latitude ~28.5°) is approximately 28-30 degrees
    setTiltAngle(28);
    // Optimal azimuth for maximum sun exposure (south-facing)
    setAzimuthAngle(180);
  };

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

      {/* Sun Angle Adjustment Controls */}
      <div className="mb-6 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <RotateCw className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-50">Panel Orientation</h4>
          </div>
          <button
            onClick={handleOptimize}
            className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors"
          >
            <Maximize2 className="w-3 h-3" />
            Optimize for Sun
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Tilt Angle Control */}
          <div>
            <label className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 mb-2">
              <Compass className="w-3 h-3" />
              Tilt Angle: {tiltAngle}°
            </label>
            <input
              type="range"
              min="0"
              max="90"
              value={tiltAngle}
              onChange={(e) => {
                setTiltAngle(Number(e.target.value));
                setAutoAdjust(false);
                setOptimizationMode('manual');
              }}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-600"
            />
            <div className="flex justify-between text-xs text-slate-500 dark:text-slate-500 mt-1">
              <span>0° (Flat)</span>
              <span>90° (Vertical)</span>
            </div>
          </div>

          {/* Azimuth Angle Control */}
          <div>
            <label className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 mb-2">
              <RotateCw className="w-3 h-3" />
              Azimuth: {azimuthAngle}° {azimuthAngle === 180 ? '(South)' : azimuthAngle < 180 ? '(East)' : '(West)'}
            </label>
            <input
              type="range"
              min="90"
              max="270"
              value={azimuthAngle}
              onChange={(e) => {
                setAzimuthAngle(Number(e.target.value));
                setAutoAdjust(false);
                setOptimizationMode('manual');
              }}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-600"
            />
            <div className="flex justify-between text-xs text-slate-500 dark:text-slate-500 mt-1">
              <span>90° (East)</span>
              <span>180° (South)</span>
              <span>270° (West)</span>
            </div>
          </div>
        </div>

        {/* Auto-adjust toggle */}
        <div className="mt-4 flex items-center gap-2">
          <input
            type="checkbox"
            id="auto-adjust"
            checked={autoAdjust}
            onChange={(e) => {
              setAutoAdjust(e.target.checked);
              if (e.target.checked) {
                setOptimizationMode('auto');
              }
            }}
            className="w-4 h-4 text-amber-600 bg-slate-100 border-slate-300 rounded focus:ring-amber-500 focus:ring-2"
          />
          <label htmlFor="auto-adjust" className="text-xs text-slate-600 dark:text-slate-400 cursor-pointer">
            Auto-adjust based on sun position
          </label>
        </div>

        {/* Efficiency indicator */}
        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600 dark:text-slate-400">Average Efficiency:</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">
              {averageEfficiency.toFixed(1)}%
            </span>
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

