'use client';

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
        return 'bg-green-500';
      case 'in_progress':
        return 'bg-blue-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4">Recent Actions</h2>
      
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
        
        {/* Actions */}
        <div className="space-y-6">
          {actions.map((action, index) => (
            <div key={action.id} className="relative pl-10">
              {/* Timeline dot */}
              <div
                className={`absolute left-2.5 w-3 h-3 rounded-full ${getStatusColor(
                  action.status
                )} ring-4 ring-white`}
              ></div>
              
              {/* Content */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="font-medium text-gray-900">{action.action}</div>
                  <div className="text-xs text-gray-500">{formatTime(action.timestamp)}</div>
                </div>
                <div className="text-sm text-gray-600 mb-2">{action.reason}</div>
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-xs font-semibold text-white ${getStatusColor(
                      action.status
                    )}`}
                  >
                    {action.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {actions.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📋</div>
          <div>No recent actions</div>
        </div>
      )}
    </div>
  );
}

