'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
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
  X
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

// Global state for hamburger menu (simple approach)
let menuState = { isOpen: false, listeners: new Set<() => void>() };

export const toggleMenu = () => {
  menuState.isOpen = !menuState.isOpen;
  menuState.listeners.forEach(listener => listener());
};

export const getMenuState = () => menuState.isOpen;

export function HamburgerMenuButton() {
  const [isOpen, setIsOpen] = useState(menuState.isOpen);
  
  useEffect(() => {
    const listener = () => setIsOpen(menuState.isOpen);
    menuState.listeners.add(listener);
    return () => {
      menuState.listeners.delete(listener);
    };
  }, []);
  
  return (
    <button
      onClick={toggleMenu}
      className="lg:hidden p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
      aria-label="Toggle menu"
    >
      {isOpen ? (
        <X className="w-5 h-5 text-slate-700 dark:text-slate-300" />
      ) : (
        <Menu className="w-5 h-5 text-slate-700 dark:text-slate-300" />
      )}
    </button>
  );
}

export default function HamburgerMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  // Sync with global state
  useEffect(() => {
    const listener = () => setIsOpen(menuState.isOpen);
    menuState.listeners.add(listener);
    menuState.isOpen = isOpen;
    menuState.listeners.forEach(l => l !== listener && l());
    return () => {
      menuState.listeners.delete(listener);
    };
  }, [isOpen]);

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
        menuState.isOpen = false;
        menuState.listeners.forEach(listener => listener());
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
    menuState.isOpen = false;
    menuState.listeners.forEach(listener => listener());
  }, [pathname]);

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => {
            setIsOpen(false);
            menuState.isOpen = false;
            menuState.listeners.forEach(listener => listener());
          }}
        />
      )}

      {/* Sidebar Menu */}
      <aside
        className={`
          hamburger-menu-container
          fixed top-0 left-0 h-full w-72 bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800 border-r border-slate-200 dark:border-slate-700 z-50
          transform transition-transform duration-300 ease-in-out shadow-xl
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:z-auto lg:shadow-none
          overflow-y-auto
        `}
      >
        <div className="p-6 h-full flex flex-col">
          {/* Logo */}
          <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-200 dark:border-slate-700">
            <Link href="/dashboard" className="flex items-center gap-3 group" onClick={() => {
              setIsOpen(false);
              menuState.isOpen = false;
              menuState.listeners.forEach(listener => listener());
            }}>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center shadow-lg shadow-amber-500/25 group-hover:scale-110 group-hover:shadow-amber-500/40 transition-all duration-300">
                <span className="text-2xl">☀️</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-slate-50 group-hover:opacity-80 transition-opacity">
                  SuryaDrishti
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Solar Forecasting</p>
              </div>
            </Link>
            {/* Close button for mobile */}
            <button
              onClick={() => {
                setIsOpen(false);
                menuState.isOpen = false;
                menuState.listeners.forEach(listener => listener());
              }}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              aria-label="Close menu"
            >
              <X className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => {
                    setIsOpen(false);
                    menuState.isOpen = false;
                    menuState.listeners.forEach(listener => listener());
                  }}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group
                    ${active
                      ? 'bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/20 text-amber-700 dark:text-amber-300 font-semibold shadow-sm border-l-4 border-amber-500'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-50 hover:shadow-sm'
                    }
                  `}
                >
                  <Icon className={`w-5 h-5 ${active ? 'text-amber-600 dark:text-amber-400' : 'text-slate-500 dark:text-slate-400'} stroke-[1.5] group-hover:scale-110 transition-transform`} />
                  <span className="flex-1">{item.name}</span>
                  {item.badge && (
                    <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full animate-pulse">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
}
