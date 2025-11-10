'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import ProfilePictureUpload from '@/components/ProfilePictureUpload';
import { ArrowLeft, User, Mail, Shield, Calendar, Bell } from 'lucide-react';

function SettingsContent() {
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Get token from localStorage
    const storedToken = localStorage.getItem('token');
    setToken(storedToken);
  }, []);

  const handleUpload = async (file: File) => {
    if (!token) {
      setError('Not authenticated');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const { getApiUrl } = await import('@/lib/get-api-url');
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/auth/upload-profile-picture`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload profile picture');
      }

      const data = await response.json();
      setSuccess('Profile picture uploaded successfully!');
      
      // Refresh user data
      const userResponse = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        // Update user in context/localStorage
        const updatedUser = {
          ...user,
          profile_picture: userData.profile_picture,
        };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        window.location.reload(); // Simple refresh for now
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload profile picture');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!token) {
      setError('Not authenticated');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const { getApiUrl } = await import('@/lib/get-api-url');
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/auth/profile-picture`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete profile picture');
      }

      setSuccess('Profile picture deleted successfully!');
      
      // Refresh user data (reuse apiUrl from above)
      const userResponse = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        const updatedUser = {
          ...user,
          profile_picture: null,
        };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        window.location.reload();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete profile picture');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="glass border-b border-slate-200/50 dark:border-slate-800/50 sticky top-0 z-50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center gap-3 group">
              <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors" />
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-slate-50">Settings</h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">Manage your account</p>
              </div>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 py-8">
        {/* Profile Picture Section */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 mb-6 card-hover">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            Profile Picture
          </h2>
          
          <div className="flex items-center gap-6">
            <ProfilePictureUpload
              currentPicture={user?.profile_picture}
              onUpload={handleUpload}
              onDelete={handleDelete}
              size="lg"
            />
            <div className="flex-1">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                Upload a profile picture to personalize your account. Supported formats: JPG, PNG, GIF, WebP
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-500">
                Maximum file size: 5MB. Image will be automatically resized to 400x400px.
              </p>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
            </div>
          )}

          {success && (
            <div className="mt-4 p-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg">
              <p className="text-sm text-emerald-800 dark:text-emerald-300">{success}</p>
            </div>
          )}
        </div>

        {/* Account Information */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 mb-6 card-hover">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-4 flex items-center gap-2">
            <Mail className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            Account Information
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1 block">
                Username
              </label>
              <div className="text-base font-medium text-slate-900 dark:text-slate-50">
                {user?.username || 'N/A'}
              </div>
            </div>
            
            <div>
              <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1 block">
                Email
              </label>
              <div className="text-base font-medium text-slate-900 dark:text-slate-50">
                {user?.email || 'N/A'}
              </div>
              {user?.is_verified === false && (
                <div className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                  Email not verified. Check your inbox for verification link.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Subscription & Trial */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 mb-6 card-hover">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            Subscription & Trial
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1 block">
                Current Plan
              </label>
              <div className="inline-flex items-center px-3 py-1.5 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
                <span className="text-sm font-semibold text-amber-700 dark:text-amber-300 capitalize">
                  {user?.plan || 'trial'}
                </span>
              </div>
            </div>
            
            {user?.trialEndDate && (
              <div>
                <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1 block">
                  Trial End Date
                </label>
                <div className="text-base font-medium text-slate-900 dark:text-slate-50">
                  {new Date(user.trialEndDate).toLocaleDateString()}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 card-hover">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-4 flex items-center gap-2">
            <Bell className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            Notifications
          </h2>
          
          <div className="space-y-3">
            <Link
              href="/settings/notifications"
              className="block text-sm text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 transition-colors"
            >
              Manage Notification Preferences
            </Link>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Configure SMS and email alerts for your microgrid
            </p>
          </div>
        </div>

        {/* Security */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 card-hover">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            Security
          </h2>
          
          <div className="space-y-3">
            <Link
              href="/forgot-password"
              className="block text-sm text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 transition-colors"
            >
              Change Password
            </Link>
            <button
              onClick={logout}
              className="block text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}



