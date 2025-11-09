'use client';

import { useTheme } from '@/contexts/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative inline-flex h-10 w-20 items-center rounded-full bg-gray-300 dark:bg-gray-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      aria-label="Toggle dark mode"
    >
      <span
        className={`inline-block h-8 w-8 transform rounded-full bg-white dark:bg-gray-900 shadow-lg transition-transform duration-300 ${
          theme === 'dark' ? 'translate-x-11' : 'translate-x-1'
        }`}
      >
        <span className="flex h-full w-full items-center justify-center">
          {theme === 'dark' ? (
            <span className="text-gray-400 text-xs font-bold">D</span>
          ) : (
            <span className="text-yellow-500 text-xs font-bold">L</span>
          )}
        </span>
      </span>
    </button>
  );
}



