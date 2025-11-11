'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { generateSchedule, getSchedules, Schedule, ScheduleGenerateRequest, getDevices, Device } from '@/lib/api-client';
import { Calendar, RefreshCw, Download, TrendingUp, Battery, Zap, Sun, Droplet, AlertCircle } from 'lucide-react';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function SchedulePageContent() {
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    loadSchedule();
    loadDevices();
  }, [selectedDate]);

  const loadDevices = async () => {
    try {
      const deviceList = await getDevices(DEFAULT_MICROGRID_ID, false);
      setDevices(deviceList);
    } catch (error) {
      console.error('Failed to load devices:', error);
    }
  };

  const loadSchedule = async () => {
    try {
      setLoading(true);
      const schedules = await getSchedules(DEFAULT_MICROGRID_ID, selectedDate, 1);
      if (schedules.length > 0) {
        setSchedule(schedules[0]);
      } else {
        setSchedule(null);
      }
    } catch (error) {
      console.error('Failed to load schedule:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      const request: ScheduleGenerateRequest = {
        date: selectedDate,
        use_forecast: true,
      };
      const newSchedule = await generateSchedule(DEFAULT_MICROGRID_ID, request);
      setSchedule(newSchedule);
    } catch (error) {
      console.error('Failed to generate schedule:', error);
      alert('Failed to generate schedule. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
  };

  const getPowerSourceColor = (slot: any) => {
    if (slot.generator_power_kw > 0.1) return 'bg-red-500';
    if (slot.grid_import_kw > 0.1) return 'bg-purple-500';
    if (slot.grid_export_kw > 0.1) return 'bg-cyan-500'; // Grid export (selling to grid)
    if (slot.battery_discharge_kw > 0.1) return 'bg-blue-500';
    if (slot.solar_generation_kw > 0.1) return 'bg-green-500';
    return 'bg-gray-300';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  const scheduleSlots = schedule?.schedule_data?.schedule || [];
  const metrics = schedule?.schedule_data?.metrics || schedule?.optimization_metrics;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">Schedule Calendar</h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              View and manage your optimized energy schedule
            </p>
          </div>
          <div className="flex gap-4">
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
            />
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="flex items-center gap-2 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors disabled:opacity-50"
            >
              {generating ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Calendar className="w-5 h-5" />
                  Generate Schedule
                </>
              )}
            </button>
          </div>
        </div>

        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <div className="flex items-center gap-3 mb-2">
                <Sun className="w-5 h-5 text-amber-600" />
                <span className="text-sm text-slate-600 dark:text-slate-400">Solar Utilization</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                {metrics.solar_utilization_percent.toFixed(1)}%
              </p>
            </div>
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <span className="text-sm text-slate-600 dark:text-slate-400">Cost Savings</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                ₹{metrics.estimated_cost_savings.toFixed(0)}
              </p>
            </div>
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <div className="flex items-center gap-3 mb-2">
                <Battery className="w-5 h-5 text-blue-600" />
                <span className="text-sm text-slate-600 dark:text-slate-400">Battery Efficiency</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                {metrics.battery_cycle_efficiency.toFixed(1)}%
              </p>
            </div>
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <div className="flex items-center gap-3 mb-2">
                <Zap className="w-5 h-5 text-purple-600" />
                <span className="text-sm text-slate-600 dark:text-slate-400">Grid Reduction</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                {metrics.grid_import_reduction_percent.toFixed(1)}%
              </p>
            </div>
          </div>
        )}

        {metrics && metrics.grid_export_revenue !== undefined && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <div className="flex items-center gap-3 mb-2">
                <Zap className="w-5 h-5 text-cyan-600" />
                <span className="text-sm text-slate-600 dark:text-slate-400">Grid Export Revenue</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                ₹{metrics.grid_export_revenue.toFixed(2)}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {metrics.grid_export_energy_kwh.toFixed(2)} kWh exported
              </p>
            </div>
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="w-5 h-5 text-emerald-600" />
                <span className="text-sm text-slate-600 dark:text-slate-400">Carbon Reduction</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                {metrics.carbon_footprint_reduction_kg.toFixed(1)} kg
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">CO₂ equivalent</p>
            </div>
          </div>
        )}

        {schedule ? (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-50 mb-2">
                Schedule for {new Date(selectedDate).toLocaleDateString()}
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {scheduleSlots.length} time slots • Generated {new Date(schedule.created_at).toLocaleString()}
              </p>
            </div>

            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {scheduleSlots.map((slot, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-4 p-4 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                >
                  <div className="w-24 text-sm font-medium text-slate-600 dark:text-slate-400">
                    {formatTime(slot.time)}
                  </div>
                  <div className="flex-1 grid grid-cols-6 gap-4">
                    <div>
                      <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Solar</div>
                      <div className="text-sm font-semibold text-green-600 dark:text-green-400">
                        {slot.solar_generation_kw.toFixed(1)} kW
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Load</div>
                      <div className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                        {slot.total_load_kw.toFixed(1)} kW
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Battery</div>
                      <div className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                        {slot.battery_charge_kw > 0
                          ? `+${slot.battery_charge_kw.toFixed(1)}`
                          : slot.battery_discharge_kw
                          ? `-${slot.battery_discharge_kw.toFixed(1)}`
                          : '0'} kW
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        {(slot.battery_soc * 100).toFixed(0)}% SOC
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Grid Import</div>
                      <div className="text-sm font-semibold text-purple-600 dark:text-purple-400">
                        {slot.grid_import_kw > 0.01 ? `${slot.grid_import_kw.toFixed(1)} kW` : '0 kW'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Grid Export</div>
                      <div className="text-sm font-semibold text-cyan-600 dark:text-cyan-400">
                        {slot.grid_export_kw > 0.01 ? `${slot.grid_export_kw.toFixed(1)} kW` : '0 kW'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Generator</div>
                      <div className="text-sm font-semibold text-red-600 dark:text-red-400">
                        {slot.generator_power_kw.toFixed(1)} kW
                      </div>
                    </div>
                  </div>
                  <div className="w-48">
                    {slot.devices.length > 0 && (
                      <div className="text-xs text-slate-500 dark:text-slate-400 mt-2 space-y-1">
                        <div className="font-medium">Active Devices:</div>
                        {slot.devices.map((device, i) => {
                          const isPump = device.is_irrigation_pump || 
                                        device.name.toLowerCase().includes('pump') ||
                                        device.name.toLowerCase().includes('irrigation');
                          const powerSource = device.power_source || 'unknown';
                          const getSourceColor = (source: string) => {
                            if (source.includes('solar')) return 'text-green-600 dark:text-green-400';
                            if (source.includes('battery')) return 'text-blue-600 dark:text-blue-400';
                            if (source.includes('grid')) return 'text-purple-600 dark:text-purple-400';
                            if (source.includes('generator')) return 'text-red-600 dark:text-red-400';
                            return 'text-slate-600 dark:text-slate-400';
                          };
                          const getSourceIcon = (source: string) => {
                            if (source.includes('solar')) return '☀️';
                            if (source.includes('battery')) return '🔋';
                            if (source.includes('grid')) return '⚡';
                            if (source.includes('generator')) return '🛢️';
                            return '';
                          };
                          
                          return (
                            <div key={i} className="text-xs">
                              • {device.name} ({device.power_kw.toFixed(1)} kW)
                              {isPump && powerSource && (
                                <span className={`ml-1 ${getSourceColor(powerSource)}`} title={`Power source: ${powerSource}`}>
                                  {getSourceIcon(powerSource)} {powerSource}
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                    {/* Check for delayed irrigation pumps */}
                    {(() => {
                      const irrigationPumps = devices.filter(d => 
                        (d.device_type === 'flexible' || d.device_type === 'optional') &&
                        (d.name.toLowerCase().includes('pump') || 
                         d.name.toLowerCase().includes('irrigation') ||
                         d.device_type === 'flexible')
                      );
                      const activeDeviceIds = slot.devices.map(d => d.id);
                      const delayedPumps = irrigationPumps.filter(p => 
                        p.is_active && !activeDeviceIds.includes(p.id)
                      );
                      
                      if (delayedPumps.length > 0) {
                        return (
                          <div className="mt-2 p-2 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded text-xs">
                            <div className="flex items-center gap-1 text-amber-700 dark:text-amber-300 font-medium mb-1">
                              <AlertCircle className="w-3 h-3" />
                              Delayed Pumps:
                            </div>
                            {delayedPumps.map((pump, i) => (
                              <div key={i} className="text-amber-600 dark:text-amber-400">
                                • {pump.name}
                              </div>
                            ))}
                            <div className="text-amber-600 dark:text-amber-400 mt-1 text-[10px]">
                              (Delayed due to forecasted power drop)
                            </div>
                          </div>
                        );
                      }
                      return null;
                    })()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-12 text-center">
            <Calendar className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50 mb-2">
              No Schedule Found
            </h3>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              Generate an optimized schedule for {new Date(selectedDate).toLocaleDateString()}
            </p>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors disabled:opacity-50"
            >
              {generating ? 'Generating...' : 'Generate Schedule'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default function SchedulePage() {
  return (
    <ProtectedRoute>
      <SchedulePageContent />
    </ProtectedRoute>
  );
}

