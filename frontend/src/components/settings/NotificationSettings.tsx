'use client';

import { useState, useEffect } from 'react';
import { getNotificationPreferences, updateNotificationPreferences, sendTestNotification } from '@/lib/api-client';
import type { NotificationPreferences, NotificationPreferenceRequest } from '@/types/notifications';
import { Bell, Phone, Mail, AlertTriangle, AlertCircle, Info, Cloud } from 'lucide-react';

interface NotificationSettingsProps {
  microgridId: string;
}

export default function NotificationSettings({ microgridId }: NotificationSettingsProps) {
  const [prefs, setPrefs] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadPreferences();
  }, [microgridId]);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getNotificationPreferences(microgridId);
      setPrefs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load preferences');
      console.error('Failed to load preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!prefs) return;
    
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    try {
      const updateData: NotificationPreferenceRequest = {
        phone_number: prefs.phone_number,
        email: prefs.email,
        enable_sms: prefs.enable_sms,
        enable_email: prefs.enable_email,
        enable_critical_alerts: prefs.enable_critical_alerts,
        enable_warning_alerts: prefs.enable_warning_alerts,
        enable_info_alerts: prefs.enable_info_alerts,
        enable_forecast_updates: prefs.enable_forecast_updates,
      };
      
      const updated = await updateNotificationPreferences(microgridId, updateData);
      setPrefs(updated);
      setSuccess('Preferences saved successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setError(null);
    setSuccess(null);
    
    try {
      await sendTestNotification(microgridId);
      setSuccess('Test notification sent! Check your phone/email.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send test notification');
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600 mx-auto"></div>
          <p className="mt-4 text-sm text-slate-600 dark:text-slate-400">Loading preferences...</p>
        </div>
      </div>
    );
  }

  if (!prefs) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
        <div className="text-center py-8">
          <p className="text-red-600 dark:text-red-400">Error loading preferences</p>
          <button
            onClick={loadPreferences}
            className="mt-4 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 space-y-6">
      <div className="flex items-center gap-2">
        <Bell className="w-5 h-5 text-slate-600 dark:text-slate-400" />
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50">Notification Settings</h2>
      </div>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
        </div>
      )}

      {success && (
        <div className="p-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg">
          <p className="text-sm text-emerald-800 dark:text-emerald-300">{success}</p>
        </div>
      )}

      {/* Contact Information */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            <Phone className="w-4 h-4 inline mr-2" />
            Phone Number (E.164 format, e.g., +919876543210)
          </label>
          <input
            type="tel"
            value={prefs.phone_number || ''}
            onChange={(e) => setPrefs({ ...prefs, phone_number: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50 focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="+919876543210"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            <Mail className="w-4 h-4 inline mr-2" />
            Email Address
          </label>
          <input
            type="email"
            value={prefs.email || ''}
            onChange={(e) => setPrefs({ ...prefs, email: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50 focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="operator@example.com"
          />
        </div>
      </div>

      {/* Notification Channels */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
          Notification Channels
        </h3>
        
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={prefs.enable_sms}
            onChange={(e) => setPrefs({ ...prefs, enable_sms: e.target.checked })}
            className="w-5 h-5 text-amber-600 border-slate-300 rounded focus:ring-amber-500"
          />
          <div>
            <span className="text-sm font-medium text-slate-900 dark:text-slate-50">Enable SMS Notifications</span>
            <p className="text-xs text-slate-500 dark:text-slate-400">Receive alerts via text message</p>
          </div>
        </label>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={prefs.enable_email}
            onChange={(e) => setPrefs({ ...prefs, enable_email: e.target.checked })}
            className="w-5 h-5 text-amber-600 border-slate-300 rounded focus:ring-amber-500"
          />
          <div>
            <span className="text-sm font-medium text-slate-900 dark:text-slate-50">Enable Email Notifications</span>
            <p className="text-xs text-slate-500 dark:text-slate-400">Receive alerts via email</p>
          </div>
        </label>
      </div>

      {/* Alert Types */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
          Alert Types
        </h3>
        
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={prefs.enable_critical_alerts}
            onChange={(e) => setPrefs({ ...prefs, enable_critical_alerts: e.target.checked })}
            className="w-5 h-5 text-amber-600 border-slate-300 rounded focus:ring-amber-500"
          />
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <div>
              <span className="text-sm font-medium text-slate-900 dark:text-slate-50">Critical Alerts</span>
              <p className="text-xs text-slate-500 dark:text-slate-400">System failures, outages, critical issues</p>
            </div>
          </div>
        </label>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={prefs.enable_warning_alerts}
            onChange={(e) => setPrefs({ ...prefs, enable_warning_alerts: e.target.checked })}
            className="w-5 h-5 text-amber-600 border-slate-300 rounded focus:ring-amber-500"
          />
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-500" />
            <div>
              <span className="text-sm font-medium text-slate-900 dark:text-slate-50">Warning Alerts</span>
              <p className="text-xs text-slate-500 dark:text-slate-400">Battery low, high load, performance issues</p>
            </div>
          </div>
        </label>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={prefs.enable_info_alerts}
            onChange={(e) => setPrefs({ ...prefs, enable_info_alerts: e.target.checked })}
            className="w-5 h-5 text-amber-600 border-slate-300 rounded focus:ring-amber-500"
          />
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-500" />
            <div>
              <span className="text-sm font-medium text-slate-900 dark:text-slate-50">Info Alerts</span>
              <p className="text-xs text-slate-500 dark:text-slate-400">General system updates and information</p>
            </div>
          </div>
        </label>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={prefs.enable_forecast_updates}
            onChange={(e) => setPrefs({ ...prefs, enable_forecast_updates: e.target.checked })}
            className="w-5 h-5 text-amber-600 border-slate-300 rounded focus:ring-amber-500"
          />
          <div className="flex items-center gap-2">
            <Cloud className="w-4 h-4 text-sky-500" />
            <div>
              <span className="text-sm font-medium text-slate-900 dark:text-slate-50">Forecast Updates</span>
              <p className="text-xs text-slate-500 dark:text-slate-400">Daily forecast summaries and updates</p>
            </div>
          </div>
        </label>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex-1 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
        <button
          onClick={handleTest}
          disabled={testing || !prefs.enable_sms}
          className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {testing ? 'Sending...' : 'Send Test'}
        </button>
      </div>
    </div>
  );
}

