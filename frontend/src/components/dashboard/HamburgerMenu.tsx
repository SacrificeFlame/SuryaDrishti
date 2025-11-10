'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { 
  LayoutDashboard, 
  Cloud, 
  Battery, 
  Bell, 
  Activity, 
  TrendingUp, 
  Map,
  Settings,
  BarChart3,
  Zap,
  Menu,
  X,
  Power
} from 'lucide-react';
import { API_BASE_URL_NO_SUFFIX } from '@/lib/api-client';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

export default function HamburgerMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const navItems: NavItem[] = [
    { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Forecast', href: '/dashboard/forecast', icon: Cloud },
    { name: 'Battery Scheduler', href: '/dashboard/battery-scheduler', icon: Battery },
    { name: 'Alerts', href: '/dashboard/alerts', icon: Bell },
    { name: 'System Status', href: '/dashboard/system-status', icon: Activity },
    { name: 'Performance', href: '/dashboard/performance', icon: TrendingUp },
    { name: 'Cloud Map', href: '/dashboard/cloud-map', icon: Map },
    { name: 'Reports', href: '/reports', icon: BarChart3 },
    { name: 'Devices', href: '/devices', icon: Zap },
    { name: 'Configuration', href: '/configuration', icon: Settings },
  ];

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname?.startsWith(href);
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (isOpen && !target.closest('.hamburger-menu-container')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Close menu when route changes
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  return (
    <>
      {/* Hamburger Button - Fixed position for mobile, visible in sidebar for desktop */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          hamburger-menu-container 
          fixed top-4 left-4 z-50 lg:hidden
          p-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800
          shadow-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors
        `}
        aria-label="Toggle menu"
      >
        {isOpen ? (
          <X className="w-6 h-6 text-slate-700 dark:text-slate-300" />
        ) : (
          <Menu className="w-6 h-6 text-slate-700 dark:text-slate-300" />
        )}
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Menu */}
      <aside
        className={`
          hamburger-menu-container
          fixed top-0 left-0 h-full w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 z-50
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:z-auto
          overflow-y-auto
        `}
      >
        <div className="p-6 h-full flex flex-col">
          {/* Logo */}
          <div className="flex items-center justify-between mb-8">
            <Link href="/dashboard" className="flex items-center gap-3 group" onClick={() => setIsOpen(false)}>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center shadow-lg shadow-amber-500/25 group-hover:scale-105 transition-transform duration-300">
                <span className="text-xl">☀️</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-900 dark:text-slate-50 group-hover:opacity-80 transition-opacity">
                  SuryaDrishti
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Solar Forecasting</p>
              </div>
            </Link>
            {/* Close button for mobile */}
            <button
              onClick={() => setIsOpen(false)}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Close menu"
            >
              <X className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group
                    ${active
                      ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 font-semibold border-l-4 border-amber-500'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-50'
                    }
                  `}
                >
                  <Icon className={`w-5 h-5 ${active ? 'text-amber-600 dark:text-amber-400' : ''} stroke-[1.5]`} />
                  <span className="flex-1">{item.name}</span>
                  {item.badge && (
                    <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* User Profile & Logout */}
          <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-3 mb-4">
              {user?.profile_picture ? (
                <img
                  src={user.profile_picture.startsWith('/') ? `${API_BASE_URL_NO_SUFFIX}${user.profile_picture}` : user.profile_picture}
                  alt={user.username}
                  className="w-10 h-10 rounded-full border-2 border-slate-200 dark:border-slate-700 object-cover"
                />
              ) : (
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center border-2 border-slate-200 dark:border-slate-700">
                  <span className="text-white text-sm font-bold">
                    {user?.username?.[0]?.toUpperCase() || 'U'}
                  </span>
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-slate-900 dark:text-slate-50 truncate">{user?.username || 'User'}</div>
                <div className="text-xs text-slate-500 dark:text-slate-400 truncate">{user?.email || 'N/A'}</div>
              </div>
            </div>
            <button
              onClick={() => {
                setIsOpen(false);
                logout();
              }}
              className="flex items-center gap-3 px-4 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-red-100 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 w-full transition-colors"
            >
              <Power className="w-5 h-5 stroke-[1.5]" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

