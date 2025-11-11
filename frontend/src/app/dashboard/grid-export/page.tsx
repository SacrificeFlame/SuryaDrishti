'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import HamburgerMenu, { HamburgerMenuButton } from '@/components/dashboard/HamburgerMenu';
import AccountPanel from '@/components/dashboard/AccountPanel';
import ThemeToggle from '@/components/ThemeToggle';
import GridExportSection from '@/components/dashboard/GridExportSection';
import { getMicrogridInfo } from '@/lib/api-client';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function GridExportContent() {
  const { user } = useAuth();
  const [location, setLocation] = useState({ lat: 28.4595, lon: 77.0266 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadLocation() {
      try {
        setLoading(true);
        setError(null);
        const microgridInfo = await getMicrogridInfo(DEFAULT_MICROGRID_ID);
        setLocation({ lat: microgridInfo.latitude, lon: microgridInfo.longitude });
      } catch (err) {
        console.error('Failed to load location:', err);
        setError(err instanceof Error ? err.message : 'Failed to load location');
      } finally {
        setLoading(false);
      }
    }

    loadLocation();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex">
      <HamburgerMenu />
      
      <div className="flex-1 flex flex-col lg:ml-0">
        {/* Header */}
        <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30">
          <div className="px-4 sm:px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 sm:gap-4">
                <HamburgerMenuButton />
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5" />
                </Link>
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-50">Grid Energy Export</h1>
                  <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
                    Sell unused energy back to the grid
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 sm:gap-4">
                <AccountPanel />
                <ThemeToggle />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            {error && (
              <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-sm font-semibold text-red-800 dark:text-red-300 mb-2">
                  Error: Failed to load location
                </p>
                <p className="text-xs text-red-700 dark:text-red-400">
                  {error}
                </p>
              </div>
            )}

            {loading ? (
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-lg p-12 text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
                <p className="mt-4 text-slate-600 dark:text-slate-400">Loading grid providers...</p>
              </div>
            ) : (
              <GridExportSection
                microgridId={DEFAULT_MICROGRID_ID}
                latitude={location.lat}
                longitude={location.lon}
                onProviderSelected={() => {
                  // Optionally refresh or show success message
                  console.log('Grid provider selected successfully');
                }}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function GridExportPage() {
  return (
    <ProtectedRoute>
      <GridExportContent />
    </ProtectedRoute>
  );
}

