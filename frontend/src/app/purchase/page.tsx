'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import ThemeToggle from '@/components/ThemeToggle';

export default function PurchasePage() {
  const { theme } = useTheme();
  const { startTrial, isAuthenticated } = useAuth();
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState('professional');
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [isStartingTrial, setIsStartingTrial] = useState(false);

  const plans = {
    starter: {
      name: 'Starter',
      monthlyPrice: 9999,
      yearlyPrice: 99990,
      features: [
        'Up to 3 microgrids',
        '60-minute forecasts',
        'Basic alerts',
        'Email support',
        'API access',
        'Standard SLA',
      ],
    },
    professional: {
      name: 'Professional',
      monthlyPrice: 24999,
      yearlyPrice: 249990,
      features: [
        'Up to 10 microgrids',
        'Advanced forecasting',
        'Smart alerts & actions',
        'Priority support',
        'Custom integrations',
        'Performance analytics',
        '99.9% SLA',
      ],
    },
    enterprise: {
      name: 'Enterprise',
      monthlyPrice: 0,
      yearlyPrice: 0,
      features: [
        'Unlimited microgrids',
        'Custom ML models',
        'Dedicated support',
        'On-site training',
        'SLA guarantee',
        'Custom features',
        '24/7 support',
      ],
    },
  };

  const selectedPlanData = plans[selectedPlan as keyof typeof plans];
  const price = billingCycle === 'monthly' 
    ? selectedPlanData.monthlyPrice 
    : selectedPlanData.yearlyPrice;
  const savings = billingCycle === 'yearly' ? Math.round(selectedPlanData.monthlyPrice * 12 * 0.17) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-yellow-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-3xl">☀️</span>
              <span className="text-xl font-bold bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">
                SuryaDrishti
              </span>
            </Link>
            <div className="flex items-center gap-6">
              <Link href="/" className="text-gray-700 dark:text-gray-300 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors">
                Home
              </Link>
              <Link href="/dashboard" className="text-gray-700 dark:text-gray-300 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors">
                Dashboard
              </Link>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </nav>

      <div className="pt-24 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
              Choose Your Plan
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-6">
              Start with a 14-day free trial. No credit card required.
            </p>
            
            {/* Billing Toggle */}
            <div className="inline-flex items-center gap-4 bg-gray-100 dark:bg-gray-800 p-1 rounded-full">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-full font-semibold transition-all ${
                  billingCycle === 'monthly'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-md'
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-6 py-2 rounded-full font-semibold transition-all ${
                  billingCycle === 'yearly'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-md'
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                Yearly
                {billingCycle === 'yearly' && (
                  <span className="ml-2 text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">
                    Save 17%
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* Plan Selection */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {Object.entries(plans).map(([key, plan]) => (
              <button
                key={key}
                onClick={() => setSelectedPlan(key)}
                className={`p-6 rounded-2xl border-2 text-left transition-all ${
                  selectedPlan === key
                    ? 'border-yellow-500 dark:border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 shadow-lg'
                    : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">{plan.name}</h3>
                  {selectedPlan === key && (
                    <span className="text-2xl">✓</span>
                  )}
                </div>
                <div className="mb-4">
                  {plan.monthlyPrice === 0 ? (
                    <span className="text-3xl font-bold text-gray-900 dark:text-white">Custom</span>
                  ) : (
                    <>
                      <span className="text-3xl font-bold text-gray-900 dark:text-white">
                        ₹{billingCycle === 'monthly' ? plan.monthlyPrice.toLocaleString() : plan.yearlyPrice.toLocaleString()}
                      </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        /{billingCycle === 'monthly' ? 'month' : 'year'}
                      </span>
                    </>
                  )}
                </div>
                <ul className="space-y-2">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <span className="text-green-500 mt-0.5">✓</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </button>
            ))}
          </div>

          {/* Checkout Form */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 md:p-12">
            <h2 className="text-2xl font-bold mb-8 text-gray-900 dark:text-white">Complete Your Purchase</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              {/* Left Column - Order Summary */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Order Summary</h3>
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 mb-6">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-gray-700 dark:text-gray-300">{selectedPlanData.name} Plan</span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {price === 0 ? 'Custom Pricing' : `₹${price.toLocaleString()}`}
                    </span>
                  </div>
                  {billingCycle === 'yearly' && savings > 0 && (
                    <div className="flex justify-between items-center text-green-600 dark:text-green-400 text-sm mb-4">
                      <span>Yearly Savings</span>
                      <span className="font-semibold">₹{savings.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-gray-900 dark:text-white">
                        {billingCycle === 'monthly' ? 'Monthly Total' : 'Yearly Total'}
                      </span>
                      <span className="text-2xl font-bold text-gray-900 dark:text-white">
                        {price === 0 ? 'Contact Sales' : `₹${price.toLocaleString()}`}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Free Trial Info */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">🎁</span>
                    <div>
                      <div className="font-semibold text-blue-900 dark:text-blue-300 mb-1">14-Day Free Trial</div>
                      <div className="text-sm text-blue-700 dark:text-blue-400">
                        Start your free trial today. No credit card required. Cancel anytime.
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column - Contact Form */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Contact Information</h3>
                <form className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                      placeholder="John Doe"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                      placeholder="john@example.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                      placeholder="+91 98765 43210"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Organization Name
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                      placeholder="Your Organization"
                    />
                  </div>
                  {selectedPlan === 'enterprise' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Number of Microgrids
                      </label>
                      <input
                        type="number"
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                        placeholder="10+"
                      />
                    </div>
                  )}
                </form>
              </div>
            </div>

            {/* Terms and Submit */}
            <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-start gap-3 mb-6">
                <input
                  type="checkbox"
                  id="terms"
                  className="mt-1 w-4 h-4 text-yellow-500 border-gray-300 rounded focus:ring-yellow-500"
                />
                <label htmlFor="terms" className="text-sm text-gray-600 dark:text-gray-400">
                  I agree to the{' '}
                  <Link href="#" className="text-yellow-600 dark:text-yellow-400 hover:underline">
                    Terms of Service
                  </Link>{' '}
                  and{' '}
                  <Link href="#" className="text-yellow-600 dark:text-yellow-400 hover:underline">
                    Privacy Policy
                  </Link>
                </label>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                {selectedPlan === 'enterprise' ? (
                  <button className="flex-1 bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200">
                    Contact Sales Team
                  </button>
                ) : (
                  <button
                    onClick={async () => {
                      setIsStartingTrial(true);
                      if (!isAuthenticated) {
                        router.push('/login?startTrial=true');
                      } else {
                        startTrial();
                        router.push('/dashboard');
                      }
                    }}
                    disabled={isStartingTrial}
                    className="flex-1 bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isStartingTrial ? 'Starting Trial...' : 'Start Free Trial'}
                  </button>
                )}
                <Link
                  href="/login"
                  className="flex-1 text-center bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200"
                >
                  {isAuthenticated ? 'Go to Dashboard' : 'Login First'}
                </Link>
              </div>
              <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
                🔒 Secure checkout. Your information is encrypted and secure.
              </p>
            </div>
          </div>

          {/* Trust Badges */}
          <div className="mt-12 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Trusted by microgrids across India</p>
            <div className="flex flex-wrap justify-center items-center gap-8 text-gray-400 dark:text-gray-600">
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>ISO 27001 Certified</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>99.9% Uptime SLA</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>24/7 Support</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Money-Back Guarantee</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

