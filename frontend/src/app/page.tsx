'use client';

import Link from 'next/link';
import { useTheme } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';

export default function LandingPage() {
  const { theme } = useTheme();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-yellow-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <span className="text-3xl">☀️</span>
              <span className="text-xl font-bold bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">
                SuryaDrishti
              </span>
            </div>
            <div className="flex items-center gap-6">
              <Link href="#features" className="text-gray-700 dark:text-gray-300 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors">
                Features
              </Link>
              <Link href="#pricing" className="text-gray-700 dark:text-gray-300 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors">
                Pricing
              </Link>
              <Link href="/login" className="text-gray-700 dark:text-gray-300 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors">
                Login
              </Link>
              <ThemeToggle />
              <Link
                href="/purchase"
                className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-6 py-2 rounded-full font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-8 inline-block">
            <span className="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 px-4 py-2 rounded-full text-sm font-semibold">
              ⚡ Real-Time Solar Forecasting
            </span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 bg-clip-text text-transparent">
            Power the Future of
            <br />
            Rural Energy
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
            AI-powered solar forecasting for microgrids. Predict cloud movements, optimize energy storage, and prevent power outages with 87% accuracy.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/purchase"
              className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-4 rounded-full text-lg font-semibold hover:shadow-xl transform hover:scale-105 transition-all duration-200"
            >
              Start Free Trial
            </Link>
            <Link
              href="/login"
              className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-8 py-4 rounded-full text-lg font-semibold border-2 border-gray-300 dark:border-gray-700 hover:border-yellow-500 dark:hover:border-yellow-500 transition-all duration-200"
            >
              View Demo
            </Link>
          </div>
          <div className="mt-12 flex justify-center items-center gap-8 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>No Credit Card Required</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>14-Day Free Trial</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Cancel Anytime</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-white/50 dark:bg-gray-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
              Powerful Features for Smart Energy Management
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              Everything you need to optimize your solar microgrid operations
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: '🌥️',
                title: 'Real-Time Cloud Tracking',
                description: 'AI-powered cloud detection and motion prediction using satellite imagery. Track cloud movements up to 60 minutes ahead.',
              },
              {
                icon: '📊',
                title: 'Probabilistic Forecasts',
                description: 'P10/P50/P90 quantile predictions for risk assessment. Plan with confidence using statistical forecasting.',
              },
              {
                icon: '🚨',
                title: 'Smart Alerts',
                description: 'Automatic alerts for significant power drops (>20%). Get notified before issues impact your grid.',
              },
              {
                icon: '🔋',
                title: 'Battery Optimization',
                description: 'Intelligent battery management recommendations. Maximize storage efficiency and reduce diesel usage.',
              },
              {
                icon: '📈',
                title: 'Performance Analytics',
                description: 'Track forecast accuracy, diesel savings, and CO₂ reduction. Comprehensive metrics dashboard.',
              },
              {
                icon: '🌍',
                title: 'Rural-Focused',
                description: 'Designed specifically for rural Indian microgrids. Works offline and with limited connectivity.',
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-200 dark:border-gray-700"
              >
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-yellow-500 to-orange-500">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 text-center text-white">
            {[
              { value: '87%', label: 'Forecast Accuracy' },
              { value: '₹45K+', label: 'Avg Monthly Savings' },
              { value: '125kg', label: 'CO₂ Avoided Daily' },
              { value: '99.2%', label: 'System Uptime' },
            ].map((stat, index) => (
              <div key={index}>
                <div className="text-5xl font-bold mb-2">{stat.value}</div>
                <div className="text-lg opacity-90">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              Choose the plan that fits your microgrid needs
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: 'Starter',
                price: '₹9,999',
                period: '/month',
                description: 'Perfect for small microgrids',
                features: [
                  'Up to 3 microgrids',
                  '60-minute forecasts',
                  'Basic alerts',
                  'Email support',
                  'API access',
                ],
                cta: 'Start Free Trial',
                popular: false,
              },
              {
                name: 'Professional',
                price: '₹24,999',
                period: '/month',
                description: 'For growing operations',
                features: [
                  'Up to 10 microgrids',
                  'Advanced forecasting',
                  'Smart alerts & actions',
                  'Priority support',
                  'Custom integrations',
                  'Performance analytics',
                ],
                cta: 'Start Free Trial',
                popular: true,
              },
              {
                name: 'Enterprise',
                price: 'Custom',
                period: '',
                description: 'For large deployments',
                features: [
                  'Unlimited microgrids',
                  'Custom ML models',
                  'Dedicated support',
                  'On-site training',
                  'SLA guarantee',
                  'Custom features',
                ],
                cta: 'Contact Sales',
                popular: false,
              },
            ].map((plan, index) => (
              <div
                key={index}
                className={`bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg border-2 ${
                  plan.popular
                    ? 'border-yellow-500 dark:border-yellow-500 transform scale-105'
                    : 'border-gray-200 dark:border-gray-700'
                }`}
              >
                {plan.popular && (
                  <div className="bg-yellow-500 text-white text-xs font-bold px-3 py-1 rounded-full inline-block mb-4">
                    MOST POPULAR
                  </div>
                )}
                <h3 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">{plan.name}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">{plan.description}</p>
                <div className="mb-6">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">{plan.price}</span>
                  <span className="text-gray-600 dark:text-gray-400">{plan.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex} className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/purchase"
                  className={`block w-full text-center py-3 rounded-lg font-semibold transition-all duration-200 ${
                    plan.popular
                      ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white hover:shadow-lg'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Transform Your Energy Management?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join hundreds of microgrids already using SuryaDrishti to optimize their operations
          </p>
          <Link
            href="/purchase"
            className="inline-block bg-white text-blue-600 px-8 py-4 rounded-full text-lg font-semibold hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            Start Your Free Trial Today
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">☀️</span>
                <span className="text-xl font-bold text-white">SuryaDrishti</span>
              </div>
              <p className="text-sm">
                AI-powered solar forecasting for rural microgrids in India.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/login" className="hover:text-white transition-colors">Login</Link></li>
                <li><Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white transition-colors">Documentation</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">API Reference</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Help Center</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>© 2024 SuryaDrishti. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
