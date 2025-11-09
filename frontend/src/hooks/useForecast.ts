/**
 * React Hooks for Forecast API
 * Provides easy-to-use hooks for fetching forecast data
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  getNGBoostForecast, 
  getHybridForecast, 
  getMicrogridForecast,
} from '@/services/forecastApi';
import type {
  NGBoostForecastResponse,
  MicrogridForecastResponse,
  HybridForecastResponse,
} from '@/types/forecast';

/**
 * Hook for NGBoost forecast (general purpose)
 */
export function useNGBoostForecast(
  lat: number | null,
  lon: number | null,
  options: {
    horizonHours?: number;
    trainingDays?: number;
    retrain?: boolean;
    enabled?: boolean;
  } = {}
) {
  const [forecast, setForecast] = useState<NGBoostForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = useCallback(async () => {
    if (!lat || !lon || options.enabled === false) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getNGBoostForecast(lat, lon, options);
      setForecast(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch forecast';
      setError(errorMessage);
      // Only log errors in development mode
      if (process.env.NODE_ENV === 'development') {
        console.error('[Forecast] Error:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [lat, lon, options.horizonHours, options.trainingDays, options.retrain, options.enabled]);

  useEffect(() => {
    fetchForecast();
  }, [fetchForecast]);

  return { forecast, loading, error, refetch: fetchForecast };
}

/**
 * Hook for Hybrid forecast (best accuracy)
 */
export function useHybridForecast(
  lat: number | null,
  lon: number | null,
  options: {
    horizonHours?: number;
    useSatellite?: boolean;
    trainingDays?: number;
    enabled?: boolean;
  } = {}
) {
  const [forecast, setForecast] = useState<HybridForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = useCallback(async () => {
    if (!lat || !lon || options.enabled === false) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getHybridForecast(lat, lon, options);
      setForecast(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch forecast';
      setError(errorMessage);
      console.error('[Forecast] Error:', err);
    } finally {
      setLoading(false);
    }
  }, [lat, lon, options.horizonHours, options.useSatellite, options.trainingDays, options.enabled]);

  useEffect(() => {
    fetchForecast();
  }, [fetchForecast]);

  return { forecast, loading, error, refetch: fetchForecast };
}

/**
 * Hook for Microgrid forecast (recommended for microgrids)
 * Includes auto-refresh functionality
 */
export function useMicrogridForecast(
  microgridId: string | null,
  options: {
    horizonHours?: number;
    trainingDays?: number;
    retrain?: boolean;
    enabled?: boolean;
    autoRefresh?: boolean;
    refreshInterval?: number; // milliseconds
  } = {}
) {
  const [forecast, setForecast] = useState<MicrogridForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = useCallback(async () => {
    if (!microgridId || options.enabled === false) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getMicrogridForecast(microgridId, options);
      setForecast(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch forecast';
      setError(errorMessage);
      // Only log errors in development mode
      if (process.env.NODE_ENV === 'development') {
        console.error('[Microgrid Forecast] Error:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [microgridId, options.horizonHours, options.trainingDays, options.retrain, options.enabled]);

  useEffect(() => {
    fetchForecast();
  }, [fetchForecast]);

  // Auto-refresh if enabled
  useEffect(() => {
    if (options.autoRefresh && microgridId && options.enabled !== false) {
      const interval = setInterval(
        fetchForecast,
        options.refreshInterval || 15 * 60 * 1000 // Default: 15 minutes
      );
      return () => clearInterval(interval);
    }
  }, [fetchForecast, options.autoRefresh, options.refreshInterval, microgridId, options.enabled]);

  return { forecast, loading, error, refetch: fetchForecast };
}
