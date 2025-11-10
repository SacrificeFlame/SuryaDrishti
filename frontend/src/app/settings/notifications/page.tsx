'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import NotificationSettings from '@/components/settings/NotificationSettings';
import { ArrowLeft, Bell } from 'lucide-react';
import { 
  getNotificationPreferences, 
  updateNotificationPreferences,
  sendTestNotification,
  API_BASE_URL 
} from '@/lib/api-client';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function NotificationPreferencesContent() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<any>(null);
  const [testSending, setTestSending] = useState(false);

  useEffect(() => {
    async function loadPreferences() {
      try {
        setLoading(true);
        setError(null);
        const prefs = await getNotificationPreferences(DEFAULT_MICROGRID_ID);
        setPreferences(prefs);
      } catch (err) {
        console.error('Failed to load notification preferences:', err);
        setError('Failed to load notification preferences');
        // Set default preferences
        setPreferences({
          phone_number: '',
          email: user?.email || '',
          sms_enabled: false,
          email_enabled: true,
          alert_types: {
            critical: true,
            warning: true,
            info: false,
          },
        });
      } finally {
        setLoading(false);
      }
    }

    loadPreferences();
  }, [user]);

  const handleSave = async (updatedPreferences: any) => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      
      const updated = await updateNotificationPreferences(DEFAULT_MICROGRID_ID, updatedPreferences);
      setPreferences(updated);
      setSuccess('Notification preferences saved successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to save notification preferences:', err);
      setError(err instanceof Error ? err.message : 'Failed to save notification preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async () => {
    try {
      setTestSending(true);
      setError(null);
      setSuccess(null);
      
      await sendTestNotification(DEFAULT_MICROGRID_ID);
      setSuccess('Test notification sent! Check your phone/email.');
      
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      console.error('Failed to send test notification:', err);
      setError(err instanceof Error ? err.message : 'Failed to send test notification');
    } finally {
      setTestSending(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
          <p className="mt-4 text-slate-600 dark:text-slate-400">Loading notification preferences...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="glass border-b border-slate-200/50 dark:border-slate-800/50 sticky top-0 z-50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/settings" className="flex items-center gap-3 group">
              <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors" />
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                <div>
                  <h1 className="text-xl font-bold text-slate-900 dark:text-slate-50">Notification Preferences</h1>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Configure alerts and notifications</p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg p-4">
            <p className="text-sm text-emerald-800 dark:text-emerald-300">{success}</p>
          </div>
        )}

        {preferences && (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <NotificationSettings microgridId={DEFAULT_MICROGRID_ID} />
          </div>
        )}
      </main>
    </div>
  );
}

export default function NotificationPreferencesPage() {
  return (
    <ProtectedRoute>
      <NotificationPreferencesContent />
    </ProtectedRoute>
  );
}
