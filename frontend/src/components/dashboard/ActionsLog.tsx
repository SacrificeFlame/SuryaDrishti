'use client';

import { CheckCircle2, Clock, AlertCircle, XCircle, FileText } from 'lucide-react';

interface Action {
  id: number;
  timestamp: string;
  action: string;
  reason: string;
  status: string;
}

interface ActionsLogProps {
  actions: Action[];
}

export default function ActionsLog({ actions }: ActionsLogProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-500';
      case 'in_progress':
        return 'bg-blue-500';
      case 'pending':
        return 'bg-amber-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-slate-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircle2;
      case 'in_progress':
        return Clock;
      case 'pending':
        return AlertCircle;
      case 'failed':
        return XCircle;
      default:
        return FileText;
    }
  };

  const getStatusIconColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-emerald-600 dark:text-emerald-400';
      case 'in_progress':
        return 'text-blue-600 dark:text-blue-400';
      case 'pending':
        return 'text-amber-600 dark:text-amber-400';
      case 'failed':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-slate-600 dark:text-slate-400';
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 card-hover">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
          <FileText className="w-5 h-5 text-slate-600 dark:text-slate-400 stroke-[1.5]" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-1">Recent Actions</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">System activity log</p>
        </div>
      </div>
      
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700"></div>
        
        {/* Actions */}
        <div className="space-y-4">
          {actions.map((action, index) => {
            const IconComponent = getStatusIcon(action.status);
            const iconColor = getStatusIconColor(action.status);
            return (
              <div key={action.id} className="relative pl-14">
                {/* Timeline dot with icon */}
                <div className={`absolute left-3.5 w-5 h-5 rounded-lg bg-white dark:bg-slate-900 border-2 ${getStatusColor(action.status)} border-white dark:border-slate-900 flex items-center justify-center`}>
                  <IconComponent className={`w-3 h-3 text-white stroke-[2]`} />
                </div>
                
                {/* Content */}
                <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                  <div className="flex justify-between items-start mb-2">
                    <div className="font-medium text-slate-900 dark:text-slate-50">{action.action}</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">{formatTime(action.timestamp)}</div>
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400 mb-2">{action.reason}</div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-block px-2.5 py-1 rounded-lg text-xs font-semibold text-white ${getStatusColor(
                        action.status
                      )}`}
                    >
                      {action.status}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {actions.length === 0 && (
        <div className="text-center py-12 text-slate-500 dark:text-slate-400">
          <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto mb-3 border border-slate-200 dark:border-slate-700">
            <FileText className="w-6 h-6 text-slate-400 dark:text-slate-500 stroke-[1.5]" />
          </div>
          <div className="text-sm font-semibold mb-1">No recent actions</div>
          <div className="text-xs">System activity will appear here</div>
        </div>
      )}
    </div>
  );
}

