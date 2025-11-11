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
  latitude?: number;
  longitude?: number;
}

// Calculate sunrise and sunset times for a given date and location
function calculateSunriseSunset(lat: number, lon: number, date: Date): { sunrise: Date; sunset: Date } {
  // Convert latitude and longitude to radians
  const latRad = (lat * Math.PI) / 180;
  
  // Calculate day of year
  const start = new Date(date.getFullYear(), 0, 0);
  const dayOfYear = Math.floor((date.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
  
  // Solar declination angle
  const declination = 23.45 * Math.sin((360 * (284 + dayOfYear) / 365) * Math.PI / 180) * Math.PI / 180;
  
  // Hour angle for sunrise/sunset
  const hourAngle = Math.acos(-Math.tan(latRad) * Math.tan(declination));
  
  // Convert hour angle to time (in hours from noon)
  const sunriseHour = 12 - (hourAngle * 180 / Math.PI) / 15;
  const sunsetHour = 12 + (hourAngle * 180 / Math.PI) / 15;
  
  // Create sunrise and sunset dates
  const sunrise = new Date(date);
  sunrise.setHours(Math.floor(sunriseHour), Math.round((sunriseHour % 1) * 60), 0, 0);
  
  const sunset = new Date(date);
  sunset.setHours(Math.floor(sunsetHour), Math.round((sunsetHour % 1) * 60), 0, 0);
  
  // Adjust for longitude (rough approximation: 4 minutes per degree)
  const timeOffset = (lon / 15) * 60; // minutes
  sunrise.setMinutes(sunrise.getMinutes() + timeOffset);
  sunset.setMinutes(sunset.getMinutes() + timeOffset);
  
  return { sunrise, sunset };
}

// Check if current time is between sunrise and sunset
function isDaytime(lat: number, lon: number, currentTime: Date = new Date()): boolean {
  try {
    const { sunrise, sunset } = calculateSunriseSunset(lat, lon, currentTime);
    // Use exact sunrise/sunset times - no buffer
    // Panels turn ON at sunrise and turn OFF at sunset
    return currentTime >= sunrise && currentTime <= sunset;
  } catch (error) {
    // If calculation fails, fallback to approximate daytime (6 AM to 6 PM)
    const hour = currentTime.getHours();
    return hour >= 6 && hour < 18;
  }
}

export default function SolarPanelsVisualization({ 
  totalPower = 0, 
  panelCount = 24,
  latitude = 28.4595, // Default to Rajasthan coordinates
  longitude = 77.0266
}: SolarPanelsVisualizationProps) {
  const [panels, setPanels] = useState<SolarPanel[]>([]);
  const [tiltAngle, setTiltAngle] = useState(30); // Default 30 degrees tilt
  const [azimuthAngle, setAzimuthAngle] = useState(180); // Default 180 degrees (south)
  const [autoAdjust, setAutoAdjust] = useState(true); // Auto-adjust based on sun position
  const [optimizationMode, setOptimizationMode] = useState<'manual' | 'auto' | 'optimal'>('optimal');
  const [isCurrentlyDaytime, setIsCurrentlyDaytime] = useState(true);

  // Check if it's currently daytime (update every minute)
  // Use actual sunrise/sunset calculation - don't rely on power data for daytime detection
  useEffect(() => {
    const checkDaytime = () => {
      const calculatedDaytime = isDaytime(latitude, longitude);
      // Use actual time of day calculation, not power data
      // Power data should only indicate generation during daytime, not determine daytime
      setIsCurrentlyDaytime(calculatedDaytime);
    };
    
    checkDaytime(); // Check immediately
    const interval = setInterval(checkDaytime, 60000); // Check every minute
    
    return () => clearInterval(interval);
  }, [latitude, longitude]);

  // Calculate optimal angle based on time of day and sun position
  useEffect(() => {
    if (autoAdjust && optimizationMode === 'auto' && isCurrentlyDaytime) {
      const now = new Date();
      const hour = now.getHours();
      const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 0).getTime()) / 86400000);
      
      // Calculate sun elevation (simplified)
      const latRad = latitude * Math.PI / 180;
      const declination = 23.45 * Math.sin((360 * (284 + dayOfYear) / 365) * Math.PI / 180) * Math.PI / 180;
      const hourAngle = (hour - 12) * 15 * Math.PI / 180;
      const elevation = Math.asin(
        Math.sin(latRad) * Math.sin(declination) +
        Math.cos(latRad) * Math.cos(declination) * Math.cos(hourAngle)
      ) * 180 / Math.PI;
      
      // Optimal tilt is approximately equal to latitude, adjusted for season
      const optimalTilt = Math.max(0, Math.min(90, latitude - (declination * 180 / Math.PI) + (elevation > 0 ? elevation * 0.3 : 0)));
      setTiltAngle(Math.round(optimalTilt));
      
      // Azimuth tracks sun position (180 = south, optimal for northern hemisphere)
      const optimalAzimuth = hour < 12 ? 180 - (12 - hour) * 15 : 180 + (hour - 12) * 15;
      setAzimuthAngle(Math.max(90, Math.min(270, optimalAzimuth)));
    }
  }, [autoAdjust, optimizationMode, isCurrentlyDaytime, latitude]);

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
    // Panels are ONLY active during daytime (between sunrise and sunset)
    // Power data (totalPower) only affects how much power is generated, not whether panels are active
    const generatedPanels: SolarPanel[] = Array.from({ length: panelCount }, (_, i) => {
      const panelAngle = tiltAngle + (Math.random() - 0.5) * 5; // Slight variation
      const panelAzimuth = azimuthAngle + (Math.random() - 0.5) * 10; // Slight variation
      const powerMultiplier = calculatePowerMultiplier(panelAngle, panelAzimuth);
      
      // Calculate individual panel power
      // Panels only generate power during daytime (after sunrise, before sunset)
      let panelPower = 0;
      if (isCurrentlyDaytime) {
        // During daytime: use totalPower if available, otherwise estimate based on capacity
        if (totalPower > 0) {
          // Distribute totalPower across all panels with slight variations
          panelPower = (totalPower / panelCount) * powerMultiplier * (0.85 + Math.random() * 0.3);
        } else {
          // During daytime with no power data, estimate based on capacity (50kW default)
          const estimatedCapacity = 50; // kW
          panelPower = (estimatedCapacity / panelCount) * powerMultiplier * 0.5 * (0.8 + Math.random() * 0.4);
        }
      } else {
        // After sunset or before sunrise: panels are OFF, no power generation
        panelPower = 0;
      }
      
      // Calculate efficiency based on power output
      const maxPanelPower = (totalPower || 50) / panelCount;
      const efficiency = maxPanelPower > 0 && isCurrentlyDaytime ? (panelPower / maxPanelPower) * 0.20 : 0; // 20% max efficiency
      
      return {
        id: i + 1,
        power: panelPower,
        // Panels are active ONLY during daytime (between sunrise and sunset)
        // After sunset or before sunrise, all panels are inactive
        status: (isCurrentlyDaytime && panelPower > 0) ? 'active' as const : 'inactive' as const,
        efficiency: efficiency,
        angle: panelAngle,
        azimuth: panelAzimuth,
      };
    });
    setPanels(generatedPanels);
  }, [totalPower, panelCount, tiltAngle, azimuthAngle, isCurrentlyDaytime]);

  const activePanels = panels.filter(p => p.status === 'active').length;
  const totalGenerated = panels.reduce((sum, p) => sum + p.power, 0);
  const averageEfficiency = panels.length > 0 
    ? (panels.reduce((sum, p) => sum + p.efficiency, 0) / panels.length) * 100 
    : 0;

  const handleOptimize = () => {
    if (!isCurrentlyDaytime) {
      // Can't optimize at night, but set to optimal day angles
      setTiltAngle(Math.round(latitude)); // Optimal tilt equals latitude
      setAzimuthAngle(180); // South-facing
      return;
    }
    
    setOptimizationMode('optimal');
    setAutoAdjust(true);
    // Calculate optimal angles for maximum sun exposure
    // Optimal tilt for location is approximately equal to latitude
    setTiltAngle(Math.round(latitude));
    // Optimal azimuth for maximum sun exposure (south-facing in northern hemisphere)
    setAzimuthAngle(180);
  };

  // Get sunrise and sunset times for display
  const { sunrise, sunset } = calculateSunriseSunset(latitude, longitude, new Date());
  const sunriseTime = sunrise.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  const sunsetTime = sunset.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

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
            {/* During daytime: show power, during nighttime: show 0 */}
            {isCurrentlyDaytime ? (totalPower > 0 ? totalPower : totalGenerated).toFixed(1) : '0.0'} kW
          </div>
          {!isCurrentlyDaytime && (
            <div className="text-xs text-slate-400 dark:text-slate-500 mt-1">
              Nighttime - Panels Off (Sunrise: {sunriseTime}, Sunset: {sunsetTime})
            </div>
          )}
          {isCurrentlyDaytime && (
            <div className="text-xs text-slate-400 dark:text-slate-500 mt-1">
              Daytime - Generating (Sunset: {sunsetTime})
            </div>
          )}
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
                  panel.status === 'active' && isCurrentlyDaytime
                    ? 'text-amber-600 dark:text-amber-400' 
                    : 'text-slate-400 dark:text-slate-500'
                }`} 
              />
              <div className={`text-[8px] mt-1 font-semibold ${
                panel.status === 'active' && isCurrentlyDaytime
                  ? 'text-amber-700 dark:text-amber-300' 
                  : 'text-slate-500 dark:text-slate-400'
              }`}>
                {panel.status === 'active' && isCurrentlyDaytime && panel.power > 0 
                  ? `${panel.power.toFixed(1)}kW` 
                  : 'OFF'}
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

