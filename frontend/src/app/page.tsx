'use client';

import Link from 'next/link';
import { useTheme } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';
import { Cloud, TrendingUp, Bell, Battery, BarChart3, MapPin } from 'lucide-react';

export default function LandingPage() {
  const { theme } = useTheme();

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      {/* Navigation */}
      <nav className="fixed top-0 w-full glass border-b border-slate-200/50 dark:border-slate-800/50 z-50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center shadow-lg shadow-amber-500/25">
                <span className="text-xl">☀️</span>
              </div>
              <span className="text-lg font-bold gradient-text">
                SuryaDrishti
              </span>
            </div>
            <div className="flex items-center gap-6">
              <Link href="#features" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-amber-600 dark:hover:text-amber-400 transition-colors hidden sm:block">
                Features
              </Link>
              <Link href="#pricing" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-amber-600 dark:hover:text-amber-400 transition-colors hidden sm:block">
                Pricing
              </Link>
              <Link href="/login" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-amber-600 dark:hover:text-amber-400 transition-colors">
                Login
              </Link>
              <ThemeToggle />
              <Link
                href="/register"
                className="relative bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:shadow-xl hover:shadow-amber-500/30 transition-all duration-300 transform hover:scale-[1.02] overflow-hidden group"
              >
                <span className="relative z-10">Get Started</span>
                <div className="absolute inset-0 bg-gradient-to-r from-amber-600 to-orange-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-40 pb-32 px-6 lg:px-8 bg-white dark:bg-slate-950">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-6xl md:text-8xl font-bold mb-8 tracking-tight leading-[1.1]">
            <span className="bg-gradient-to-r from-amber-600 via-orange-600 to-pink-600 bg-clip-text text-transparent">
              Take Control of Your
            </span>
            <br />
            <span className="text-slate-900 dark:text-slate-50">Solar Energy</span>
          </h1>
          <p className="text-xl md:text-2xl text-slate-600 dark:text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed font-light">
            SuryaDrishti offers a seamless, secure experience for managing your solar microgrid. Real-time forecasting, optimized energy storage, and premium design.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/register"
              className="relative bg-gradient-to-r from-amber-500 to-orange-500 text-white px-10 py-4 rounded-xl text-lg font-semibold hover:shadow-2xl hover:shadow-amber-500/30 transition-all duration-300 transform hover:scale-[1.02] overflow-hidden group"
            >
              <span className="relative z-10">Get started now</span>
              <div className="absolute inset-0 bg-gradient-to-r from-amber-600 to-orange-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-6 lg:px-8 bg-white dark:bg-slate-950">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <p className="text-xs uppercase tracking-[0.15em] text-amber-600 dark:text-amber-400 mb-6 font-semibold letter-spacing-wider">
              Simplicity, performance, and security, empowering you to navigate the digital world with confidence and agility.
            </p>
            <h2 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">
              <span className="bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                Why Choose
              </span>
              <span className="text-slate-900 dark:text-slate-50"> SuryaDrishti?</span>
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto font-light">
              Benefits designed to provide a seamless, secure, and accessible experience for all users.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: 'Real-Time Cloud Tracking',
                description: 'AI-powered cloud detection and motion prediction using satellite imagery. Track cloud movements up to 60 minutes ahead.',
                icon: Cloud,
                iconColor: 'text-sky-600 dark:text-sky-400',
                bgColor: 'from-sky-50/50 to-blue-50/30',
              },
              {
                title: 'Probabilistic Forecasts',
                description: 'P10/P50/P90 quantile predictions for risk assessment. Plan with confidence using statistical forecasting.',
                icon: TrendingUp,
                iconColor: 'text-emerald-600 dark:text-emerald-400',
                bgColor: 'from-emerald-50/50 to-teal-50/30',
              },
              {
                title: 'Smart Alerts',
                description: 'Automatic alerts for significant power drops (>20%). Get notified before issues impact your grid.',
                icon: Bell,
                iconColor: 'text-amber-600 dark:text-amber-400',
                bgColor: 'from-amber-50/50 to-orange-50/30',
              },
              {
                title: 'Battery Optimization',
                description: 'Intelligent battery management recommendations. Maximize storage efficiency and reduce diesel usage.',
                icon: Battery,
                iconColor: 'text-violet-600 dark:text-violet-400',
                bgColor: 'from-violet-50/50 to-purple-50/30',
              },
              {
                title: 'Performance Analytics',
                description: 'Track forecast accuracy, diesel savings, and CO₂ reduction. Comprehensive metrics dashboard.',
                icon: BarChart3,
                iconColor: 'text-indigo-600 dark:text-indigo-400',
                bgColor: 'from-indigo-50/50 to-blue-50/30',
              },
              {
                title: 'Rural-Focused',
                description: 'Designed specifically for rural Indian microgrids. Works offline and with limited connectivity.',
                icon: MapPin,
                iconColor: 'text-amber-600 dark:text-amber-400',
                bgColor: 'from-amber-50/50 to-yellow-50/30',
              },
            ].map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div
                  key={index}
                  className="group relative text-center p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/60 hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-300 hover:shadow-2xl hover:shadow-slate-200/50 dark:hover:shadow-slate-900/50 hover:-translate-y-1"
                >
                  <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${feature.bgColor} dark:from-slate-800/30 dark:to-slate-900/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>
                  <div className="relative">
                    <div className="w-16 h-16 rounded-xl bg-slate-100 dark:bg-slate-800 mx-auto mb-6 flex items-center justify-center border border-slate-200 dark:border-slate-700 group-hover:scale-110 transition-transform duration-300">
                      <IconComponent className={`w-8 h-8 ${feature.iconColor} stroke-[1.5]`} />
                    </div>
                    <h3 className="text-xl font-bold mb-3 text-slate-900 dark:text-slate-50 group-hover:text-slate-800 dark:group-hover:text-slate-100 transition-colors">{feature.title}</h3>
                    <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-[15px]">{feature.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* All Features Section */}
      <section className="py-32 px-6 lg:px-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">
              <span className="bg-gradient-to-r from-amber-600 via-orange-600 to-pink-600 bg-clip-text text-transparent">
                All Features,
              </span>
              <span className="text-slate-900 dark:text-slate-50"> One Platform</span>
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto font-light">
              Monitor, forecast, and optimize all your solar microgrid operations on a single platform. A seamless experience with no compromises.
            </p>
          </div>
          <div className="text-center">
            <Link
              href="/purchase"
              className="relative bg-gradient-to-r from-amber-500 to-orange-500 text-white px-10 py-4 rounded-xl text-lg font-semibold hover:shadow-2xl hover:shadow-amber-500/30 transition-all duration-300 transform hover:scale-[1.02] inline-block overflow-hidden group"
            >
              <span className="relative z-10">Get started now</span>
              <div className="absolute inset-0 bg-gradient-to-r from-amber-600 to-orange-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-32 px-6 lg:px-8 bg-white dark:bg-slate-950">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">
              <span className="text-slate-900 dark:text-slate-50">How It </span>
              <span className="bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">Works</span>
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              A simple, fast, and secure platform to manage your solar microgrid in just a few steps.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-12 mb-12">
            {[
              {
                number: '1',
                title: 'Create your account',
                description: 'Sign up easily and secure your profile in just a few steps.',
                color: 'from-blue-500 to-cyan-500',
              },
              {
                number: '2',
                title: 'Connect your microgrid',
                description: 'Link your solar system and sensors to start monitoring.',
                color: 'from-emerald-500 to-teal-500',
              },
              {
                number: '3',
                title: 'Monitor and optimize',
                description: 'Enjoy the simplicity of a platform that makes every forecast seamless in real-time.',
                color: 'from-amber-500 to-orange-500',
              },
            ].map((step, index) => (
              <div key={index} className="text-center group">
                <div className={`text-7xl font-bold bg-gradient-to-br ${step.color} bg-clip-text text-transparent mb-6 group-hover:scale-110 transition-transform duration-300`}>{step.number}</div>
                <h3 className="text-xl font-bold mb-3 text-slate-900 dark:text-slate-50">{step.title}</h3>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-[15px] font-light">{step.description}</p>
              </div>
            ))}
          </div>
          <div className="text-center">
            <Link
              href="/register"
              className="relative bg-gradient-to-r from-amber-500 to-orange-500 text-white px-10 py-4 rounded-xl text-lg font-semibold hover:shadow-2xl hover:shadow-amber-500/30 transition-all duration-300 transform hover:scale-[1.02] inline-block overflow-hidden group"
            >
              <span className="relative z-10">Create account now</span>
              <div className="absolute inset-0 bg-gradient-to-r from-amber-600 to-orange-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </Link>
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section id="pricing" className="py-32 px-6 lg:px-8 bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-950">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">
              <span className="text-slate-900 dark:text-slate-50">Simple, Transparent </span>
              <span className="bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">Pricing</span>
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              Choose the plan that fits your microgrid needs
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {[
              {
                name: 'Basic',
                price: '₹3,999',
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
                name: 'Standard',
                price: '₹7,999',
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
                name: 'Premium',
                price: '₹14,999',
                period: '/month',
                description: 'For advanced operations',
                features: [
                  'Up to 25 microgrids',
                  'Advanced ML forecasting',
                  'Real-time alerts & actions',
                  'Priority support',
                  'Advanced analytics',
                  'Dedicated account manager',
                ],
                cta: 'Start Free Trial',
                popular: false,
              },
              {
                name: 'Enterprise',
                price: '₹49,999',
                period: '/month',
                description: 'For large deployments',
                features: [
                  'Unlimited microgrids',
                  'Custom ML models',
                  'Dedicated support',
                  'On-site training',
                  'SLA guarantee',
                  '24/7 support',
                ],
                cta: 'Contact Sales',
                popular: false,
              },
            ].map((plan, index) => (
              <div
                key={index}
                className={`group relative bg-white dark:bg-slate-900 p-10 rounded-2xl shadow-xl border ${
                  plan.popular
                    ? 'border-amber-500/50 dark:border-amber-500/50 transform scale-105 shadow-2xl shadow-amber-500/10'
                    : 'border-slate-200/60 dark:border-slate-800/60 hover:border-slate-300 dark:hover:border-slate-700'
                } transition-all duration-300 hover:shadow-2xl`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-[10px] font-bold px-4 py-1.5 rounded-full uppercase tracking-wider shadow-lg">
                    MOST POPULAR
                  </div>
                )}
                <h3 className="text-2xl font-bold mb-2 text-slate-900 dark:text-slate-50">{plan.name}</h3>
                <p className="text-slate-600 dark:text-slate-400 mb-6 text-sm font-light">{plan.description}</p>
                <div className="mb-8 pb-8 border-b border-slate-200 dark:border-slate-800">
                  <span className="text-5xl font-bold text-slate-900 dark:text-slate-50">{plan.price}</span>
                  <span className="text-slate-600 dark:text-slate-400 text-lg ml-2">{plan.period}</span>
                </div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex} className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-emerald-600 dark:text-emerald-400 text-xs">✓</span>
                      </div>
                      <span className="text-slate-700 dark:text-slate-300 text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/purchase"
                  className={`block w-full text-center py-4 rounded-xl font-semibold transition-all duration-300 ${
                    plan.popular
                      ? 'relative bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:shadow-2xl hover:shadow-amber-500/30 transform hover:scale-[1.02] overflow-hidden group'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-700'
                  }`}
                >
                  {plan.popular ? (
                    <>
                      <span className="relative z-10">{plan.cta}</span>
                      <div className="absolute inset-0 bg-gradient-to-r from-amber-600 to-orange-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </>
                  ) : (
                    plan.cta
                  )}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6 lg:px-8 bg-gradient-to-br from-amber-500 via-orange-500 to-pink-500 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),transparent_50%)]"></div>
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-5xl md:text-6xl font-bold mb-6 text-white tracking-tight">
            Ready to take control of your solar energy?
          </h2>
          <p className="text-lg text-white/95 mb-12 max-w-2xl mx-auto font-light">
            Join thousands of users who trust SuryaDrishti for secure, seamless, and efficient solar microgrid management.
          </p>
          <Link
            href="/register"
            className="bg-white text-amber-600 px-10 py-4 rounded-xl text-lg font-semibold hover:shadow-2xl hover:shadow-white/20 transition-all duration-300 transform hover:scale-[1.02] inline-block"
          >
            Get started now
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 text-slate-400 py-16 px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500 flex items-center justify-center">
                  <span className="text-lg">☀️</span>
                </div>
                <span className="text-lg font-bold text-white">SuryaDrishti</span>
              </div>
              <p className="text-sm text-slate-500">
                Secure, fast, and seamless solar forecasting. SuryaDrishti makes digital energy management effortless.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Navigation</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#features" className="hover:text-white transition-colors">Why SuryaDrishti?</Link></li>
                <li><Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/login" className="hover:text-white transition-colors">Login</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Socials</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white transition-colors">Twitter (X)</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Instagram</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">LinkedIn</Link></li>
              </ul>
            </div>
            <div>
              <p className="text-sm text-slate-500">
                Created with ❤️ in India
              </p>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 text-center text-sm text-slate-500">
            <p>© 2024 SuryaDrishti. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
