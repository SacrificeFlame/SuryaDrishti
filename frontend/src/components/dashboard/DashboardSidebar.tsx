'use client';

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
  Zap
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

export default function DashboardSidebar() {
  const pathname = usePathname();

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

  return (
    <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 h-screen sticky top-0 overflow-y-auto">
      <div className="p-6">
        <Link href="/dashboard" className="flex items-center gap-3 mb-8 group">
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

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            
            return (
              <Link
                key={item.href}
                href={item.href}
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
      </div>
    </aside>
  );
}

