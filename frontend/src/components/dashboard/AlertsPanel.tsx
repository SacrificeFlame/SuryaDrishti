'use client';

import { Alert } from '@/types/forecast';

interface AlertsPanelProps {
  alerts: Alert[];
}

export default function AlertsPanel({ alerts }: AlertsPanelProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-500 text-red-900';
      case 'warning':
        return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      case 'info':
        return 'bg-blue-100 border-blue-500 text-blue-900';
      case 'success':
        return 'bg-green-100 border-green-500 text-green-900';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-900';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🚨';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      case 'success':
        return '✅';
      default:
        return '📌';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors duration-300">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Active Alerts</h2>
        <span className="bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">
          {alerts.length}
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <div className="text-4xl mb-2">✓</div>
            <div>No active alerts</div>
            <div className="text-sm">System operating normally</div>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`border-l-4 rounded-r-lg p-4 ${getSeverityColor(alert.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-2 flex-1">
                  <span className="text-xl">{getSeverityIcon(alert.severity)}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold capitalize">{alert.severity}</span>
                      <span className="text-xs opacity-75">{formatTime(alert.timestamp)}</span>
                    </div>
                    <p className="text-sm mb-2">{alert.message}</p>
                    {alert.action && (
                      <div className="bg-white bg-opacity-50 rounded p-2 text-xs">
                        <div className="font-semibold mb-1">Recommended Action:</div>
                        <div>{alert.action}</div>
                      </div>
                    )}
                  </div>
                </div>
                <button className="text-xs px-3 py-1 bg-white bg-opacity-50 hover:bg-opacity-75 rounded transition">
                  Acknowledge
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

