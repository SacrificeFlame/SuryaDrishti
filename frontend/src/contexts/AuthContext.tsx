'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

export interface User {
  id?: number;
  username: string;
  email?: string;
  profile_picture?: string | null;
  is_verified?: boolean;
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
    try {
      console.log('[Login] Attempting login for:', username);
      
      // Use OAuth2PasswordRequestForm format (username field can be email or username)
      const formData = new FormData();
      formData.append('username', username); // OAuth2 uses 'username' field for both email and username
      formData.append('password', password);

      console.log('[Login] Sending login request...');
      
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      let response;
      try {
        // Use dynamic API URL detection to handle invalid backend URLs
        const { getApiUrl } = await import('@/lib/get-api-url');
        const apiUrl = getApiUrl();
        console.log('[Login] Using API URL:', apiUrl);
        response = await fetch(`${apiUrl}/auth/login`, {
          method: 'POST',
          body: formData,
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        if (fetchError.name === 'AbortError') {
          throw new Error('Request timeout: Backend server is not responding. Please check if the server is running.');
        }
        // Handle network errors with improved error handling
        const { isNetworkError, isDNSError, getNetworkErrorMessage, logNetworkError } = await import('@/utils/networkErrorHandler');
        if (isNetworkError(fetchError) || isDNSError(fetchError)) {
          logNetworkError(fetchError, apiUrl);
          throw new Error(getNetworkErrorMessage(fetchError, apiUrl));
        }
        throw new Error(`Network error: ${fetchError.message}`);
      }

      console.log('[Login] Response status:', response.status);

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          const text = await response.text();
          console.error('[Login] Failed to parse error response:', text);
          throw new Error(`Login failed: ${response.status} ${response.statusText}`);
        }
        console.error('[Login] Login failed:', errorData.detail || errorData.message);
        throw new Error(errorData.detail || errorData.message || 'Login failed');
      }

      const tokenData = await response.json();
      console.log('[Login] Token received');
      const accessToken = tokenData.access_token;

      if (!accessToken) {
        throw new Error('No access token received');
      }

      // Store token
      localStorage.setItem('token', accessToken);

      // Fetch user info
      console.log('[Login] Fetching user info...');
      
      const userController = new AbortController();
      const userTimeoutId = setTimeout(() => userController.abort(), 10000);
      
      let userResponse;
      try {
        // Use dynamic API URL detection
        const { getApiUrl } = await import('@/lib/get-api-url');
        const apiUrl = getApiUrl();
        userResponse = await fetch(`${apiUrl}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
          signal: userController.signal,
        });
        clearTimeout(userTimeoutId);
      } catch (fetchError: any) {
        clearTimeout(userTimeoutId);
        if (fetchError.name === 'AbortError') {
          throw new Error('Request timeout: Failed to fetch user information.');
        }
        // Handle network errors with improved error handling
        const { isNetworkError, isDNSError, getNetworkErrorMessage, logNetworkError } = await import('@/utils/networkErrorHandler');
        if (isNetworkError(fetchError) || isDNSError(fetchError)) {
          logNetworkError(fetchError, apiUrl);
          throw new Error(getNetworkErrorMessage(fetchError, apiUrl));
        }
        throw new Error(`Network error: ${fetchError.message}`);
      }

      if (!userResponse.ok) {
        console.error('[Login] Failed to fetch user info:', userResponse.status);
        throw new Error('Failed to fetch user information');
      }

      const userData = await userResponse.json();
      console.log('[Login] User data received:', userData);

      // Transform to User interface
      const user: User = {
        id: userData.id,
        username: userData.username,
        email: userData.email,
        profile_picture: userData.profile_picture,
        is_verified: userData.is_verified,
        plan: userData.plan as 'trial' | 'starter' | 'professional' | 'enterprise',
        trialStartDate: userData.trial_start_date || undefined,
        trialEndDate: userData.trial_end_date || undefined,
      };

      setUser(user);
      localStorage.setItem('user', JSON.stringify(user));
      console.log('[Login] Login successful!');
      return true;
    } catch (error) {
      console.error('[Login] Login error:', error);
      
      // Fallback to admin credentials for backward compatibility
      if (username === ADMIN_CREDENTIALS.username && password === ADMIN_CREDENTIALS.password) {
        console.log('[Login] Using admin fallback');
        const userData: User = {
          username: 'admin',
          email: 'admin@suryadrishti.com',
          plan: 'trial',
        };

        const savedUser = localStorage.getItem('user');
        if (savedUser) {
          try {
            const parsedUser = JSON.parse(savedUser);
            userData.trialStartDate = parsedUser.trialStartDate || new Date().toISOString();
            userData.trialEndDate = parsedUser.trialEndDate || new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString();
            userData.plan = parsedUser.plan || 'trial';
          } catch (e) {
            userData.trialStartDate = new Date().toISOString();
            userData.trialEndDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString();
          }
        } else {
          userData.trialStartDate = new Date().toISOString();
          userData.trialEndDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString();
        }

        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        return true;
      }
      
      // Re-throw the error so the login page can display it
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
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

