import { useState, useEffect } from 'react';

export interface ForecastPoint {
  time: string;
  timestamp: string;
  p10: number;
  p50: number;
  p90: number;
  power_output: number;
}

export interface ForecastData {
  location: { lat: number; lon: number };
  timestamp: string;
  forecasts: ForecastPoint[];
  confidence: number;
  alerts: any[];
  cloud_data: any;
  current_irradiance: number;
  current_power_output: number;
}

export function useForecast(microgridId: string = 'microgrid_001') {
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/forecast/current/${microgridId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch forecast');
      }
      
      const data = await response.json();
      setForecast(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
    // Refresh every 5 minutes
    const interval = setInterval(fetchForecast, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [microgridId]);

  return { forecast, loading, error, refreshForecast: fetchForecast };
}

