/**
 * Forecast API Service
 * Handles all API calls to the forecast endpoints
 */

import type {
  NGBoostForecastResponse,
  MicrogridForecastResponse,
  HybridForecastResponse,
} from '@/types/forecast';

// Import dynamic API URL getter
import { getApiUrl } from '@/lib/get-api-url';

// Get API URL dynamically at runtime
// This handles cases where NEXT_PUBLIC_API_URL might be set to an invalid URL
function getAPI_BASE_URL(): string {
  return getApiUrl();
}

/**
 * Get NGBoost forecast for a location
 */
export async function getNGBoostForecast(
  lat: number,
  lon: number,
  options: {
    horizonHours?: number;
    trainingDays?: number;
    retrain?: boolean;
  } = {}
): Promise<NGBoostForecastResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    horizon_hours: (options.horizonHours || 24).toString(),
    training_days: (options.trainingDays || 180).toString(),
    retrain: (options.retrain || false).toString(),
  });

  const apiUrl = getAPI_BASE_URL();
  const response = await fetch(`${apiUrl}/forecast/ngboost?${params}`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Get hybrid forecast (satellite + weather)
 */
export async function getHybridForecast(
  lat: number,
  lon: number,
  options: {
    horizonHours?: number;
    useSatellite?: boolean;
    trainingDays?: number;
  } = {}
): Promise<HybridForecastResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    horizon_hours: (options.horizonHours || 24).toString(),
    use_satellite: (options.useSatellite !== false).toString(),
    training_days: (options.trainingDays || 180).toString(),
  });

  const apiUrl = getAPI_BASE_URL();
  const response = await fetch(`${apiUrl}/forecast/hybrid?${params}`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Get microgrid forecast (recommended for microgrids)
 */
export async function getMicrogridForecast(
  microgridId: string,
  options: {
    horizonHours?: number;
    trainingDays?: number;
    retrain?: boolean;
  } = {}
): Promise<MicrogridForecastResponse> {
  const params = new URLSearchParams({
    horizon_hours: (options.horizonHours || 24).toString(),
    training_days: (options.trainingDays || 180).toString(),
    retrain: (options.retrain || false).toString(),
  });

  try {
    // Add timeout to prevent hanging requests
    // Backend timeout is 45s, so frontend should wait slightly longer (50s) to receive response
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 50000); // 50 second timeout
    
    const apiUrl = getAPI_BASE_URL();
    const response = await fetch(
      `${apiUrl}/forecast/microgrid/${microgridId}?${params}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      }
    );
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      
      if (response.status === 404) {
        throw new Error(`Microgrid ${microgridId} not found`);
      }
      throw new Error(errorMessage);
    }
    
    return response.json();
  } catch (err) {
    // Handle abort (timeout)
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error('Request timeout - the external API is taking too long to respond');
    }
    // Handle network errors with improved error handling
    const { isNetworkError, isDNSError, getNetworkErrorMessage, logNetworkError } = await import('@/utils/networkErrorHandler');
    if (isNetworkError(err) || isDNSError(err)) {
      const apiUrl = getAPI_BASE_URL();
      logNetworkError(err, apiUrl);
      throw new Error(getNetworkErrorMessage(err, apiUrl));
    }
    // Re-throw if it's already an Error, otherwise wrap it
    if (err instanceof Error) {
      throw err;
    }
    throw new Error(`Failed to fetch microgrid forecast: ${String(err)}`);
  }
}

