'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { 
  User, 
  Settings, 
  LogOut, 
  ChevronDown, 
  Mail,
  Shield,
  CreditCard
} from 'lucide-react';
import { API_BASE_URL_NO_SUFFIX } from '@/lib/api-client';

export default function AccountPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
      >
        {user?.profile_picture ? (
          <img
            src={user.profile_picture.startsWith('/') ? `${API_BASE_URL_NO_SUFFIX}${user.profile_picture}` : user.profile_picture}
            alt={user.username}
            className="w-8 h-8 rounded-full border-2 border-slate-200 dark:border-slate-600 object-cover"
          />
        ) : (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center border-2 border-slate-200 dark:border-slate-600">
            <span className="text-white text-sm font-bold">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </span>
          </div>
        )}
        <span className="hidden sm:inline-block text-sm font-medium text-slate-700 dark:text-slate-300">
          {user?.username || 'User'}
        </span>
        <ChevronDown className={`w-4 h-4 text-slate-600 dark:text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-white dark:bg-slate-900 rounded-xl shadow-lg border border-slate-200 dark:border-slate-800 py-2 z-50">
          {/* User Info */}
          <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-3">
              {user?.profile_picture ? (
                <img
                  src={user.profile_picture.startsWith('/') ? `${API_BASE_URL_NO_SUFFIX}${user.profile_picture}` : user.profile_picture}
                  alt={user.username}
                  className="w-12 h-12 rounded-full border-2 border-slate-200 dark:border-slate-700 object-cover"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center border-2 border-slate-200 dark:border-slate-700">
                  <span className="text-white text-lg font-bold">
                    {user?.username?.[0]?.toUpperCase() || 'U'}
                  </span>
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-slate-900 dark:text-slate-50 truncate">
                  {user?.username || 'User'}
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400 truncate">
                  {user?.email || 'N/A'}
                </div>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="py-2">
            <Link
              href="/settings"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              <User className="w-4 h-4" />
              <span>Profile Settings</span>
            </Link>
            <Link
              href="/settings/notifications"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              <Mail className="w-4 h-4" />
              <span>Notifications</span>
            </Link>
            <Link
              href="/configuration"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              <Settings className="w-4 h-4" />
              <span>System Configuration</span>
            </Link>
            <div className="border-t border-slate-200 dark:border-slate-800 my-2"></div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 w-full text-left transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

