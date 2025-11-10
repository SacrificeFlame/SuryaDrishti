'use client';

import { useState } from 'react';
import { Alert } from '@/types/forecast';
import { AlertCircle, AlertTriangle, Info, CheckCircle2, Bell } from 'lucide-react';
import { acknowledgeAlert } from '@/lib/api-client';

interface AlertsPanelProps {
  alerts: Alert[];
  onAlertAcknowledged?: (alertId: number) => void;
}

export default function AlertsPanel({ alerts, onAlertAcknowledged }: AlertsPanelProps) {
  const [acknowledging, setAcknowledging] = useState<Set<number>>(new Set());

  const handleAcknowledge = async (alertId: number) => {
    if (acknowledging.has(alertId)) return;
    
    setAcknowledging(prev => new Set(prev).add(alertId));
    try {
      await acknowledgeAlert(alertId, true);
      if (onAlertAcknowledged) {
        onAlertAcknowledged(alertId);
      }
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
      alert('Failed to acknowledge alert. Please try again.');
    } finally {
      setAcknowledging(prev => {
        const next = new Set(prev);
        next.delete(alertId);
        return next;
      });
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'border-red-500 bg-red-50 dark:bg-red-900/20';
      case 'warning':
        return 'border-amber-500 bg-amber-50 dark:bg-amber-900/20';
      case 'info':
        return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20';
      case 'success':
        return 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20';
      default:
        return 'border-slate-500 bg-slate-50 dark:bg-slate-800/50';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return AlertCircle;
      case 'warning':
        return AlertTriangle;
      case 'info':
        return Info;
      case 'success':
        return CheckCircle2;
      default:
        return Bell;
    }
  };

  const getSeverityIconColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 dark:text-red-400';
      case 'warning':
        return 'text-amber-600 dark:text-amber-400';
      case 'info':
        return 'text-blue-600 dark:text-blue-400';
      case 'success':
        return 'text-emerald-600 dark:text-emerald-400';
      default:
        return 'text-slate-600 dark:text-slate-400';
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
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 card-hover">
      <div className="flex justify-between items-center mb-5">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-1">Active Alerts</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">System notifications</p>
        </div>
        {alerts.length > 0 && (
          <span className="bg-red-500 text-white px-2.5 py-1 rounded-lg text-xs font-bold shadow-sm">
            {alerts.length}
          </span>
        )}
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="text-center py-12 text-slate-500 dark:text-slate-400">
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center mx-auto mb-3 border border-emerald-200 dark:border-emerald-800">
              <CheckCircle2 className="w-6 h-6 text-emerald-600 dark:text-emerald-400 stroke-[1.5]" />
            </div>
            <div className="text-sm font-semibold text-emerald-600 dark:text-emerald-400 mb-1">All Systems Operational</div>
            <div className="text-xs">No active alerts</div>
          </div>
        ) : (
          alerts.map((alert) => {
            const IconComponent = getSeverityIcon(alert.severity);
            const iconColor = getSeverityIconColor(alert.severity);
            return (
              <div
                key={alert.id}
                className={`border-l-4 rounded-lg p-4 bg-slate-50 dark:bg-slate-800/50 ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`w-8 h-8 rounded-lg bg-white dark:bg-slate-900 flex items-center justify-center border border-slate-200 dark:border-slate-700 flex-shrink-0`}>
                      <IconComponent className={`w-4 h-4 ${iconColor} stroke-[1.5]`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold capitalize text-slate-900 dark:text-slate-50">{alert.severity}</span>
                        <span className="text-xs text-slate-500 dark:text-slate-400">{formatTime(alert.timestamp)}</span>
                      </div>
                      <p className="text-sm text-slate-700 dark:text-slate-300 mb-2">{alert.message}</p>
                      {alert.action && (
                        <div className="bg-white dark:bg-slate-900 rounded-lg p-2.5 text-xs border border-slate-200 dark:border-slate-700">
                          <div className="font-semibold mb-1 text-slate-900 dark:text-slate-50">Recommended Action:</div>
                          <div className="text-slate-600 dark:text-slate-400">{alert.action}</div>
                        </div>
                      )}
                    </div>
                  </div>
                  {!alert.acknowledged && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      disabled={acknowledging.has(alert.id)}
                      className="text-xs px-3 py-1.5 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 transition text-slate-700 dark:text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {acknowledging.has(alert.id) ? 'Acknowledging...' : 'Acknowledge'}
                    </button>
                  )}
                  {alert.acknowledged && (
                    <span className="text-xs px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 rounded-lg border border-emerald-200 dark:border-emerald-800">
                      Acknowledged
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

