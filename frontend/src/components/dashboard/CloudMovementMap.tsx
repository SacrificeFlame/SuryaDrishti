'use client';

import { useMemo } from 'react';
import { Satellite, Cloud, CloudRain, CloudSnow } from 'lucide-react';

interface CloudMovementMapProps {
  cloudData: {
    cloud_map: number[][];
    motion_vectors: Array<Array<{ x: number; y: number }>>;
  };
  location: { lat: number; lon: number };
}

export default function CloudMovementMap({ cloudData, location }: CloudMovementMapProps) {
  // Analyze cloud data and create statistics
  const cloudStats = useMemo(() => {
    if (!cloudData?.cloud_map) {
      return {
        clear: 0,
        thin: 0,
        thick: 0,
        storm: 0,
        total: 0,
        cloudCoverage: 0,
      };
    }

    let clear = 0;
    let thin = 0;
    let thick = 0;
    let storm = 0;
    let total = 0;

    cloudData.cloud_map.forEach((row) => {
      row.forEach((cell) => {
        total++;
        if (cell === 0) clear++;
        else if (cell === 1) thin++;
        else if (cell === 2) thick++;
        else storm++;
      });
    });

    const cloudCoverage = ((thin + thick + storm) / total) * 100;

    return {
      clear,
      thin,
      thick,
      storm,
      total,
      cloudCoverage: cloudCoverage.toFixed(1),
    };
  }, [cloudData]);

  // Calculate motion statistics
  const motionStats = useMemo(() => {
    if (!cloudData?.motion_vectors) {
      return [];
    }

    const speeds: number[] = [];
    cloudData.motion_vectors.forEach((row) => {
      row.forEach((vector) => {
        const speed = Math.sqrt(vector.x * vector.x + vector.y * vector.y);
        if (speed > 0.01) {
          speeds.push(speed);
        }
      });
    });

    // Group speeds into bins for bar chart
    const bins = Array(10).fill(0);
    const maxSpeed = Math.max(...speeds, 1);
    speeds.forEach((speed) => {
      const binIndex = Math.min(Math.floor((speed / maxSpeed) * 10), 9);
      bins[binIndex]++;
    });

    return bins;
  }, [cloudData]);

  const maxMotion = Math.max(...motionStats, 1);

  const maxCloudCount = Math.max(cloudStats.clear, cloudStats.thin, cloudStats.thick, cloudStats.storm, 1);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 card-hover">
      <div className="flex justify-between iteimage.pngms-center mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
            <Satellite className="w-5 h-5 text-slate-600 dark:text-slate-400 stroke-[1.5]" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-1">Cloud Movement Analysis</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Cloud coverage & movement statistics</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Cloud Coverage</div>
          <div className="text-lg font-bold text-slate-900 dark:text-slate-50">{cloudStats.cloudCoverage}%</div>
        </div>
      </div>

      {/* Cloud Coverage Bar Chart */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Cloud Coverage Distribution</h3>
        <div className="space-y-3">
          {/* Clear Sky */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-blue-200 dark:bg-blue-800 border border-blue-300 dark:border-blue-700"></div>
                <span className="text-xs font-medium text-slate-700 dark:text-slate-300">Clear Sky</span>
              </div>
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">{cloudStats.clear} ({((cloudStats.clear / cloudStats.total) * 100).toFixed(1)}%)</span>
            </div>
            <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-400 to-blue-500 rounded-full transition-all duration-300"
                style={{ width: `${(cloudStats.clear / maxCloudCount) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Thin Cloud */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <Cloud className="w-3 h-3 text-slate-400 dark:text-slate-500 stroke-[1.5]" />
                <span className="text-xs font-medium text-slate-700 dark:text-slate-300">Thin Cloud</span>
              </div>
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">{cloudStats.thin} ({((cloudStats.thin / cloudStats.total) * 100).toFixed(1)}%)</span>
            </div>
            <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-slate-300 to-slate-400 rounded-full transition-all duration-300"
                style={{ width: `${(cloudStats.thin / maxCloudCount) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Thick Cloud */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <CloudRain className="w-3 h-3 text-slate-500 dark:text-slate-400 stroke-[1.5]" />
                <span className="text-xs font-medium text-slate-700 dark:text-slate-300">Thick Cloud</span>
              </div>
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">{cloudStats.thick} ({((cloudStats.thick / cloudStats.total) * 100).toFixed(1)}%)</span>
            </div>
            <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-slate-500 to-slate-600 rounded-full transition-all duration-300"
                style={{ width: `${(cloudStats.thick / maxCloudCount) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Storm */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <CloudSnow className="w-3 h-3 text-slate-700 dark:text-slate-300 stroke-[1.5]" />
                <span className="text-xs font-medium text-slate-700 dark:text-slate-300">Storm</span>
              </div>
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">{cloudStats.storm} ({((cloudStats.storm / cloudStats.total) * 100).toFixed(1)}%)</span>
            </div>
            <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-slate-700 to-slate-800 rounded-full transition-all duration-300"
                style={{ width: `${(cloudStats.storm / maxCloudCount) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Motion Speed Distribution Bar Chart */}
      {motionStats.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Cloud Motion Speed Distribution</h3>
          <div className="h-48 flex items-end justify-between gap-1">
            {motionStats.map((count, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center group">
                <div
                  className="w-full bg-gradient-to-t from-amber-500 to-orange-500 rounded-t transition-all hover:from-amber-600 hover:to-orange-600 cursor-pointer"
                  style={{ height: `${(count / maxMotion) * 100}%` }}
                  title={`Speed bin ${idx + 1}: ${count} vectors`}
                ></div>
                <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1">{idx + 1}</div>
              </div>
            ))}
          </div>
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400 text-center">
            Motion speed bins (low → high)
          </div>
        </div>
      )}

      {/* Location Info */}
      <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-500 dark:text-slate-400">Location</span>
          <span className="font-mono text-slate-700 dark:text-slate-300">
            {location.lat.toFixed(4)}°N, {location.lon.toFixed(4)}°E
          </span>
        </div>
        <div className="flex items-center justify-between text-xs mt-1">
          <span className="text-slate-500 dark:text-slate-400">Total Cells Analyzed</span>
          <span className="font-semibold text-slate-700 dark:text-slate-300">{cloudStats.total}</span>
        </div>
      </div>
    </div>
  );
}
