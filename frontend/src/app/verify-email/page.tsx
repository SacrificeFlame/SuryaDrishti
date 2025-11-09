'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useTheme } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';
import { CheckCircle2, XCircle, Mail, Loader2 } from 'lucide-react';

export default function VerifyEmailPage() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const { theme } = useTheme();

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('No verification token provided');
      return;
    }

    const verifyEmail = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/auth/verify-email?token=${token}`, {
          method: 'POST',
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Verification failed');
        }

        setStatus('success');
        setMessage('Email verified successfully! You can now log in.');
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          router.push('/login?verified=true');
        }, 3000);
      } catch (err) {
        setStatus('error');
        setMessage(err instanceof Error ? err.message : 'Email verification failed');
      }
    };

    verifyEmail();
  }, [token, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-amber-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center px-4 animate-fade-in">
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-8 max-w-md w-full card-hover">
        <div className="text-center">
          {status === 'loading' && (
            <>
              <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center mx-auto mb-4 border border-blue-200 dark:border-blue-800">
                <Loader2 className="w-8 h-8 text-blue-600 dark:text-blue-400 animate-spin" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-2">Verifying Email...</h2>
              <p className="text-slate-600 dark:text-slate-400">Please wait while we verify your email address.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center mx-auto mb-4 border border-emerald-200 dark:border-emerald-800">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-2">Email Verified!</h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">{message}</p>
              <p className="text-sm text-slate-500 dark:text-slate-500">Redirecting to login page...</p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center mx-auto mb-4 border border-red-200 dark:border-red-800">
                <XCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-2">Verification Failed</h2>
              <p className="text-slate-600 dark:text-slate-400 mb-6">{message}</p>
              <div className="space-y-3">
                <Link
                  href="/login"
                  className="btn-primary inline-block w-full text-center"
                >
                  Go to Login
                </Link>
                <button
                  onClick={async () => {
                    // Resend verification email
                    const email = prompt('Enter your email address to resend verification:');
                    if (email) {
                      try {
                        const response = await fetch('http://localhost:8000/api/v1/auth/resend-verification', {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({ email }),
                        });
                        const data = await response.json();
                        alert(data.message || 'Verification email sent!');
                      } catch (err) {
                        alert('Failed to resend verification email');
                      }
                    }
                  }}
                  className="btn-secondary w-full"
                >
                  <Mail className="w-4 h-4 inline mr-2" />
                  Resend Verification Email
                </button>
              </div>
            </>
          )}
        </div>

        {/* Theme Toggle */}
        <div className="mt-6 flex justify-center">
          <ThemeToggle />
        </div>
      </div>
    </div>
  );
}



