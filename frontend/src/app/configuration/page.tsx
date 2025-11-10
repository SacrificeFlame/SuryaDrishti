'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getConfiguration, updateConfiguration, SystemConfiguration, SystemConfigurationUpdate } from '@/lib/api-client';
import { Save, Battery, Zap, Fuel, Settings, ArrowLeft } from 'lucide-react';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function ConfigurationPageContent() {
  const [config, setConfig] = useState<SystemConfiguration | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState<SystemConfigurationUpdate>({});

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      const data = await getConfiguration(DEFAULT_MICROGRID_ID);
      setConfig(data);
      setFormData({});
    } catch (error) {
      console.error('Failed to load configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const updated = await updateConfiguration(DEFAULT_MICROGRID_ID, formData);
      setConfig(updated);
      setFormData({});
      alert('Configuration saved successfully!');
    } catch (error) {
      console.error('Failed to save configuration:', error);
      alert('Failed to save configuration. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const updateField = (field: keyof SystemConfigurationUpdate, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  if (loading || !config) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  const getValue = (field: keyof SystemConfiguration) => {
    return (formData as any)[field] !== undefined ? (formData as any)[field] : (config as any)[field];
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8">
      <div className="max-w-4xl mx-auto px-6 lg:px-8">
        <div className="mb-8">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="text-sm font-medium">Back to Dashboard</span>
          </Link>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">System Configuration</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2">
            Configure battery, grid, and generator parameters for optimization
          </p>
        </div>

        <div className="space-y-6">
          {/* Battery Configuration */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Battery className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-50">Battery Settings</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Capacity (kWh)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={getValue('battery_capacity_kwh')}
                  onChange={(e) => updateField('battery_capacity_kwh', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Max Charge Rate (kW)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={getValue('battery_max_charge_rate_kw')}
                  onChange={(e) => updateField('battery_max_charge_rate_kw', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Max Discharge Rate (kW)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={getValue('battery_max_discharge_rate_kw')}
                  onChange={(e) => updateField('battery_max_discharge_rate_kw', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Efficiency (0-1)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={getValue('battery_efficiency')}
                  onChange={(e) => updateField('battery_efficiency', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Min SOC (0-1)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={getValue('battery_min_soc')}
                  onChange={(e) => updateField('battery_min_soc', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Max SOC (0-1)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={getValue('battery_max_soc')}
                  onChange={(e) => updateField('battery_max_soc', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
            </div>
          </div>

          {/* Grid Configuration */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Zap className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-50">Grid Pricing</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Peak Rate (₹/kWh)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={getValue('grid_peak_rate_per_kwh')}
                  onChange={(e) => updateField('grid_peak_rate_per_kwh', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Off-Peak Rate (₹/kWh)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={getValue('grid_off_peak_rate_per_kwh')}
                  onChange={(e) => updateField('grid_off_peak_rate_per_kwh', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Peak Hours Start (0-23)
                </label>
                <input
                  type="number"
                  min="0"
                  max="23"
                  value={config.grid_peak_hours?.start || 8}
                  onChange={(e) =>
                    updateField('grid_peak_hours', {
                      start: parseInt(e.target.value),
                      end: config.grid_peak_hours?.end || 20,
                    })
                  }
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Peak Hours End (0-23)
                </label>
                <input
                  type="number"
                  min="0"
                  max="23"
                  value={config.grid_peak_hours?.end || 20}
                  onChange={(e) =>
                    updateField('grid_peak_hours', {
                      start: config.grid_peak_hours?.start || 8,
                      end: parseInt(e.target.value),
                    })
                  }
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Grid Export Rate (₹/kWh)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={getValue('grid_export_rate_per_kwh')}
                  onChange={(e) => updateField('grid_export_rate_per_kwh', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Feed-in tariff rate for selling excess energy to grid
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Enable Grid Export
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={getValue('grid_export_enabled') ?? true}
                    onChange={(e) => updateField('grid_export_enabled', e.target.checked)}
                    className="w-5 h-5 text-amber-600 border-slate-300 rounded focus:ring-amber-500"
                  />
                  <span className="text-sm text-slate-600 dark:text-slate-400">
                    Sell surplus energy to grid when battery is full
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Generator Configuration */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Fuel className="w-6 h-6 text-red-600" />
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-50">Generator Settings</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Fuel Consumption (L/kWh)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={getValue('generator_fuel_consumption_l_per_kwh')}
                  onChange={(e) => updateField('generator_fuel_consumption_l_per_kwh', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Fuel Cost (₹/L)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={getValue('generator_fuel_cost_per_liter')}
                  onChange={(e) => updateField('generator_fuel_cost_per_liter', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Min Runtime (minutes)
                </label>
                <input
                  type="number"
                  value={getValue('generator_min_runtime_minutes')}
                  onChange={(e) => updateField('generator_min_runtime_minutes', parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Max Power (kW)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={getValue('generator_max_power_kw')}
                  onChange={(e) => updateField('generator_max_power_kw', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
            </div>
          </div>

          {/* Optimization Settings */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Settings className="w-6 h-6 text-amber-600" />
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-50">Optimization Preferences</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Optimization Mode
                </label>
                <select
                  value={getValue('optimization_mode')}
                  onChange={(e) => updateField('optimization_mode', e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                >
                  <option value="cost">Cost Minimization</option>
                  <option value="battery_longevity">Battery Longevity</option>
                  <option value="grid_independence">Grid Independence</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Safety Margin for Critical Loads (0-1)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={getValue('safety_margin_critical_loads')}
                  onChange={(e) => updateField('safety_margin_critical_loads', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleSave}
              disabled={saving || Object.keys(formData).length === 0}
              className="flex items-center gap-2 px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-5 h-5" />
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ConfigurationPage() {
  return (
    <ProtectedRoute>
      <ConfigurationPageContent />
    </ProtectedRoute>
  );
}

