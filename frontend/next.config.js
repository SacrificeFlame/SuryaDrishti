/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // Enable standalone output for Docker
  // Ensure path aliases work - use absolute path resolution
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Resolve path aliases
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(process.cwd(), 'src'),
    };
    
    // Ensure proper module resolution
    config.resolve.modules = [
      path.resolve(process.cwd(), 'src'),
      path.resolve(process.cwd(), 'node_modules'),
      'node_modules',
    ];
    
    return config;
  },
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    const baseUrl = apiUrl.replace('/api/v1', '');
    
    return [
      {
        source: '/api/backend/:path*',
        destination: `${baseUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig

