import { useState, useEffect } from 'react';

export interface Alert {
  id?: number;
  severity: string;
  message: string;
  timestamp: string;
  action?: string;
}

export interface SystemStatus {
  battery: { soc: number; voltage: number; current: number };
  diesel: { status: string; fuelLevel: number };
  loads: { critical: number; nonCritical: number };
  timestamp: string;
  recent_actions: Array<{ action: string; timestamp: string; details?: string }>;
}

export function useWebSocket() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/updates');

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'alert') {
        setAlerts((prev) => [data.payload, ...prev].slice(0, 10));
      } else if (data.type === 'system_status') {
        setSystemStatus(data.payload);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  return { alerts, systemStatus, connected };
}

