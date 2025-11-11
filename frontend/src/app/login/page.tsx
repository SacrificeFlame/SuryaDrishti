'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated, startTrial } = useAuth();
  const { theme } = useTheme();
  const router = useRouter();
  const searchParams = useSearchParams();
  const startTrialAfterLogin = searchParams.get('startTrial') === 'true';

  useEffect(() => {
    // Check for registration/verification success messages
    const registered = searchParams.get('registered');
    const verified = searchParams.get('verified');
    
    if (registered === 'true') {
      // Show success message (could add a toast notification here)
    }
    if (verified === 'true') {
      // Show verification success message
    }

    if (isAuthenticated) {
      if (startTrialAfterLogin) {
        startTrial();
      }
      router.push('/dashboard');
    }
  }, [isAuthenticated, router, startTrialAfterLogin, startTrial, searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('[Login Page] Starting login...');
      const success = await login(username, password);
      console.log('[Login Page] Login result:', success);
      if (success) {
        console.log('[Login Page] Redirecting to dashboard...');
        setLoading(false);
        router.push('/dashboard');
      } else {
        setError('Invalid username or password');
        setLoading(false);
      }
    } catch (err) {
      console.error('[Login Page] Login error:', err);
      setLoading(false);
      if (err instanceof TypeError && err.message.includes('fetch')) {
        const { getApiBaseUrl } = await import('@/lib/get-api-url');
        const apiUrl = getApiBaseUrl();
        setError(`Cannot connect to server. Please make sure the backend is running. Check browser console for API URL details.`);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-amber-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center px-4 animate-fade-in">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="w-full max-w-md animate-scale-in">
        {/* Logo */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-5">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center shadow-xl shadow-amber-500/25">
              <span className="text-4xl">☀️</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold gradient-text mb-2">
            SuryaDrishti
          </h1>
          <p className="text-slate-500 dark:text-slate-400 font-medium">Solar Forecasting Platform</p>
        </div>

        {/* Login Card */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-8 card-hover">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-2 text-center">
            Sign In
          </h2>
          <p className="text-center text-sm text-slate-500 dark:text-slate-400 mb-8">Access your dashboard</p>

          {/* Success Messages */}
          {searchParams.get('registered') === 'true' && (
            <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg">
              <p className="text-sm text-emerald-800 dark:text-emerald-300">
                {searchParams.get('onboarded') === 'true'
                  ? 'Registration and device onboarding successful! Please check your email to verify your account.'
                  : 'Registration successful! Please check your email to verify your account.'}
              </p>
            </div>
          )}
          {searchParams.get('verified') === 'true' && (
            <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg">
              <p className="text-sm text-emerald-800 dark:text-emerald-300">
                Email verified! You can now log in.
              </p>
            </div>
          )}
          {searchParams.get('passwordReset') === 'true' && (
            <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg">
              <p className="text-sm text-emerald-800 dark:text-emerald-300">
                Password reset successful! You can now log in with your new password.
              </p>
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="username" className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                Email or Username
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 dark:text-slate-500 pointer-events-none z-10" />
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="input-field"
                  style={{ paddingLeft: '3rem' }}
                  placeholder="Enter your email or username"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 dark:text-slate-500 pointer-events-none z-10" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="input-field"
                  style={{ paddingLeft: '3rem', paddingRight: '2.5rem' }}
                  placeholder="Enter your password"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300"
                  disabled={loading}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">INFO</span>
                <div className="text-sm text-blue-800 dark:text-blue-300">
                  <div className="font-semibold mb-2">Demo Credentials:</div>
                  <div className="space-y-1 text-xs">
                    <div>Username: <code className="bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded font-mono">admin</code></div>
                    <div>Password: <code className="bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded font-mono">admin@123</code></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            <div className="text-center text-sm text-slate-600 dark:text-slate-400">
              Don't have an account?{' '}
              <Link href="/register" className="text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 transition-colors font-semibold">
                Create account
              </Link>
            </div>
            <div className="text-center">
              <Link
                href="/forgot-password"
                className="text-sm text-slate-500 dark:text-slate-500 hover:text-amber-600 dark:hover:text-amber-400 transition-colors"
              >
                Forgot password?
              </Link>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-slate-500 dark:text-slate-400">
          <Link href="/" className="hover:text-amber-600 dark:hover:text-amber-400 transition-colors font-medium">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}

