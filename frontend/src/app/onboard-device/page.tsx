'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useTheme } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';
import { Sun, Battery, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';

const SOLAR_PROVIDERS = [
  { id: 'tata-power-solar', name: 'Tata Power Solar', description: 'Leading solar solutions provider' },
  { id: 'adani-solar', name: 'Adani Solar', description: 'Renewable energy solutions' },
  { id: 'loom-solar', name: 'Loom Solar', description: 'Innovative solar technology' },
];

const BATTERY_TYPES = [
  { id: 'exide', name: 'Exide', description: 'Reliable battery solutions' },
  { id: 'luminous', name: 'Luminous', description: 'Advanced battery technology' },
  { id: 'amaron', name: 'Amaron', description: 'Premium battery systems' },
];

export default function OnboardDevicePage() {
  const [selectedSolarProvider, setSelectedSolarProvider] = useState<string>('');
  const [selectedBatteryType, setSelectedBatteryType] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { theme } = useTheme();

  useEffect(() => {
    // Get user_id from URL params (set after registration)
    const userIdParam = searchParams.get('user_id');
    if (userIdParam) {
      setUserId(parseInt(userIdParam, 10));
    } else {
      // If no user_id, redirect to register
      router.push('/register');
    }
  }, [searchParams, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!selectedSolarProvider || !selectedBatteryType) {
      setError('Please select both a solar provider and battery type');
      return;
    }

    if (!userId) {
      setError('User ID not found. Please register again.');
      return;
    }

    setLoading(true);

    try {
      const { getApiUrl } = await import('@/lib/get-api-url');
      const apiUrl = getApiUrl();
      
      // Map IDs to display names
      const solarProviderMap: { [key: string]: string } = {
        'tata-power-solar': 'Tata Power Solar',
        'adani-solar': 'Adani Solar',
        'loom-solar': 'Loom Solar',
      };
      
      const batteryTypeMap: { [key: string]: string } = {
        'exide': 'Exide',
        'luminous': 'Luminous',
        'amaron': 'Amaron',
      };

      const response = await fetch(`${apiUrl}/auth/onboard-device/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          solar_provider: solarProviderMap[selectedSolarProvider],
          battery_type: batteryTypeMap[selectedBatteryType],
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save device preferences');
      }

      const data = await response.json();
      console.log('[Onboard Device] Device preferences saved:', data);
      
      setSuccess(true);
      setLoading(false);
      
      // Redirect to login after 2 seconds with success message
      setTimeout(() => {
        router.push('/login?registered=true&onboarded=true');
      }, 2000);
    } catch (err) {
      console.error('[Onboard Device] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to save device preferences. Please try again.');
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-amber-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center px-4 animate-fade-in">
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-8 max-w-md w-full card-hover">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center mx-auto mb-4 border border-emerald-200 dark:border-emerald-800">
              <CheckCircle2 className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-2">Device Onboarded Successfully!</h2>
            <p className="text-slate-600 dark:text-slate-400 mb-4">
              Your device preferences have been saved and your system is ready to use.
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-500 mb-6">
              Redirecting to login page...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-amber-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center px-4 animate-fade-in">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="w-full max-w-2xl animate-scale-in">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-5">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center shadow-xl shadow-amber-500/25">
              <span className="text-4xl">☀️</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold gradient-text mb-2">
            Device Onboarding
          </h1>
          <p className="text-slate-500 dark:text-slate-400 font-medium">
            Select your solar panel provider and battery type
          </p>
        </div>

        {/* Onboarding Card */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-8 card-hover">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
              </div>
            )}

            {/* Solar Provider Selection */}
            <div>
              <label className="block text-lg font-semibold text-slate-900 dark:text-slate-50 mb-4 flex items-center gap-2">
                <Sun className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                Solar Panel Provider
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {SOLAR_PROVIDERS.map((provider) => (
                  <button
                    key={provider.id}
                    type="button"
                    onClick={() => setSelectedSolarProvider(provider.id)}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                      selectedSolarProvider === provider.id
                        ? 'border-amber-500 bg-amber-50 dark:bg-amber-900/20 shadow-md'
                        : 'border-slate-200 dark:border-slate-700 hover:border-amber-300 dark:hover:border-amber-700 bg-white dark:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-slate-900 dark:text-slate-50">
                        {provider.name}
                      </span>
                      {selectedSolarProvider === provider.id && (
                        <CheckCircle2 className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                      )}
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      {provider.description}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Battery Type Selection */}
            <div>
              <label className="block text-lg font-semibold text-slate-900 dark:text-slate-50 mb-4 flex items-center gap-2">
                <Battery className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                Battery Type
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {BATTERY_TYPES.map((battery) => (
                  <button
                    key={battery.id}
                    type="button"
                    onClick={() => setSelectedBatteryType(battery.id)}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                      selectedBatteryType === battery.id
                        ? 'border-amber-500 bg-amber-50 dark:bg-amber-900/20 shadow-md'
                        : 'border-slate-200 dark:border-slate-700 hover:border-amber-300 dark:hover:border-amber-700 bg-white dark:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-slate-900 dark:text-slate-50">
                        {battery.name}
                      </span>
                      {selectedBatteryType === battery.id && (
                        <CheckCircle2 className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                      )}
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      {battery.description}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !selectedSolarProvider || !selectedBatteryType}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  Continue to Dashboard
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Skip Option (Optional - for demo purposes, we'll make it required) */}
          <div className="mt-6 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Already have an account?{' '}
              <Link href="/login" className="text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 transition-colors font-semibold">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

