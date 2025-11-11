'use client';

import { useState, useEffect } from 'react';
import { Zap, CheckCircle2, AlertCircle, Loader2, TrendingUp } from 'lucide-react';
import { getGridProviders, selectGridProvider, type GridProvider, type GridProviderListResponse } from '@/lib/api-client';

interface GridExportSectionProps {
  microgridId: string;
  latitude: number;
  longitude: number;
  onProviderSelected?: () => void;
}

export default function GridExportSection({
  microgridId,
  latitude,
  longitude,
  onProviderSelected,
}: GridExportSectionProps) {
  const [providers, setProviders] = useState<GridProvider[]>([]);
  const [selectedProviderId, setSelectedProviderId] = useState<string | null>(null);
  const [enableExport, setEnableExport] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadGridProviders();
  }, [microgridId, latitude, longitude]);

  const loadGridProviders = async () => {
    try {
      setLoading(true);
      setError(null);
      const response: GridProviderListResponse = await getGridProviders(microgridId, latitude, longitude);
      setProviders(response.providers);
      if (response.selected_provider_id) {
        setSelectedProviderId(response.selected_provider_id);
      }
    } catch (err) {
      console.error('Failed to load grid providers:', err);
      setError(err instanceof Error ? err.message : 'Failed to load grid providers');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProvider = async (providerId: string) => {
    if (saving) return;

    try {
      setSaving(true);
      setError(null);
      setSuccess(false);

      await selectGridProvider(microgridId, {
        provider_id: providerId,
        enable_export: enableExport,
      });

      setSelectedProviderId(providerId);
      setSuccess(true);

      if (onProviderSelected) {
        onProviderSelected();
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to select grid provider:', err);
      setError(err instanceof Error ? err.message : 'Failed to select grid provider');
    } finally {
      setSaving(false);
    }
  };

  const selectedProvider = providers.find((p) => p.id === selectedProviderId);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/20 flex items-center justify-center">
            <Zap className="w-6 h-6 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-50">Grid Energy Export</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Sell unused energy back to the grid
            </p>
          </div>
        </div>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={enableExport}
            onChange={(e) => setEnableExport(e.target.checked)}
            className="w-5 h-5 text-amber-600 border-slate-300 rounded focus:ring-amber-500 focus:ring-2"
            disabled={saving}
          />
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Enable Export
          </span>
        </label>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-red-800 dark:text-red-300">Error</p>
            <p className="text-xs text-red-700 dark:text-red-400 mt-1">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">Success</p>
            <p className="text-xs text-emerald-700 dark:text-emerald-400 mt-1">
              Grid provider selected successfully!
            </p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-amber-600 dark:text-amber-400" />
          <span className="ml-3 text-slate-600 dark:text-slate-400">Loading grid providers...</span>
        </div>
      ) : providers.length === 0 ? (
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-slate-400 dark:text-slate-500 mx-auto mb-3" />
          <p className="text-slate-600 dark:text-slate-400">No grid providers available for this location</p>
        </div>
      ) : (
        <div className="space-y-4">
          {providers.map((provider) => {
            const isSelected = selectedProviderId === provider.id;
            const isBestRate = providers.every(
              (p) => p.export_rate_per_kwh <= provider.export_rate_per_kwh
            );

            return (
              <div
                key={provider.id}
                className={`border-2 rounded-lg p-4 transition-all duration-200 cursor-pointer ${
                  isSelected
                    ? 'border-amber-500 bg-amber-50 dark:bg-amber-900/20 ring-2 ring-amber-500/20'
                    : 'border-slate-200 dark:border-slate-700 hover:border-amber-300 dark:hover:border-amber-600 bg-slate-50 dark:bg-slate-800/50'
                } ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => !saving && handleSelectProvider(provider.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                        {provider.name}
                      </h3>
                      {isBestRate && (
                        <span className="px-2 py-1 text-xs font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded-full flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          Best Rate
                        </span>
                      )}
                      {isSelected && (
                        <span className="px-2 py-1 text-xs font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded-full flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" />
                          Selected
                        </span>
                      )}
                    </div>
                    {provider.description && (
                      <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                        {provider.description}
                      </p>
                    )}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                      <div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Export Rate</div>
                        <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                          ₹{provider.export_rate_per_kwh.toFixed(2)}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">per kWh</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Peak Rate</div>
                        <div className="text-lg font-bold text-slate-700 dark:text-slate-300">
                          ₹{provider.peak_rate_per_kwh.toFixed(2)}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">per kWh</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Off-Peak Rate</div>
                        <div className="text-lg font-bold text-slate-700 dark:text-slate-300">
                          ₹{provider.off_peak_rate_per_kwh.toFixed(2)}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">per kWh</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Peak Hours</div>
                        <div className="text-lg font-bold text-slate-700 dark:text-slate-300">
                          {provider.peak_hours.start}:00 - {provider.peak_hours.end}:00
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">IST</div>
                      </div>
                    </div>
                    {provider.coverage_areas && provider.coverage_areas.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {provider.coverage_areas.map((area, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded"
                          >
                            {area}
                          </span>
                        ))}
                      </div>
                    )}
                    {provider.minimum_export_kw && provider.maximum_export_kw && (
                      <div className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                        Export capacity: {provider.minimum_export_kw} kW - {provider.maximum_export_kw} kW
                      </div>
                    )}
                  </div>
                  <div className="ml-4 flex items-center">
                    {isSelected && (
                      <CheckCircle2 className="w-6 h-6 text-amber-600 dark:text-amber-400" />
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selectedProvider && enableExport && (
        <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Currently exporting to: <span className="font-semibold">{selectedProvider.name}</span>
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Export rate: ₹{selectedProvider.export_rate_per_kwh.toFixed(2)} per kWh
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

