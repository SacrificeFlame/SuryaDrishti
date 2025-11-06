'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

export interface User {
  username: string;
  email?: string;
  trialStartDate?: string;
  trialEndDate?: string;
  plan?: 'trial' | 'starter' | 'professional' | 'enterprise';
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isTrialActive: boolean;
  trialDaysRemaining: number;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  startTrial: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Default admin credentials
const ADMIN_CREDENTIALS = {
  username: 'admin',
  password: 'admin@123',
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
    // Load user from localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
      } catch (e) {
        localStorage.removeItem('user');
      }
    }
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    // Check credentials
    if (username === ADMIN_CREDENTIALS.username && password === ADMIN_CREDENTIALS.password) {
      const userData: User = {
        username: 'admin',
        email: 'admin@suryadrishti.com',
        plan: 'trial',
      };

      // Check if user already has trial data
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        try {
          const parsedUser = JSON.parse(savedUser);
          userData.trialStartDate = parsedUser.trialStartDate || new Date().toISOString();
          userData.trialEndDate = parsedUser.trialEndDate || new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString();
          userData.plan = parsedUser.plan || 'trial';
        } catch (e) {
          // If parsing fails, start new trial
          userData.trialStartDate = new Date().toISOString();
          userData.trialEndDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString();
        }
      } else {
        // Start new trial
        userData.trialStartDate = new Date().toISOString();
        userData.trialEndDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString();
      }

      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return true;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    router.push('/login');
  };

  const startTrial = () => {
    if (user) {
      const updatedUser: User = {
        ...user,
        trialStartDate: new Date().toISOString(),
        trialEndDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
        plan: 'trial',
      };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  const isTrialActive = (): boolean => {
    if (!user || !user.trialEndDate) return false;
    const trialEnd = new Date(user.trialEndDate);
    return trialEnd > new Date();
  };

  const trialDaysRemaining = (): number => {
    if (!user || !user.trialEndDate) return 0;
    const trialEnd = new Date(user.trialEndDate);
    const now = new Date();
    const diff = trialEnd.getTime() - now.getTime();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return Math.max(0, days);
  };

  if (!mounted) {
    return null;
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isTrialActive: isTrialActive(),
        trialDaysRemaining: trialDaysRemaining(),
        login,
        logout,
        startTrial,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

