'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import NotificationSettings from '@/components/settings/NotificationSettings';
import { ArrowLeft } from 'lucide-react';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function NotificationsContent() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="glass border-b border-slate-200/50 dark:border-slate-800/50 sticky top-0 z-50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/settings" className="flex items-center gap-3 group">
              <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors" />
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-slate-50">Notification Settings</h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">Manage alerts and notifications</p>
              </div>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 py-8">
        <NotificationSettings microgridId={DEFAULT_MICROGRID_ID} />
      </main>
    </div>
  );
}

export default function NotificationsPage() {
  return (
    <ProtectedRoute>
      <NotificationsContent />
    </ProtectedRoute>
  );
}

