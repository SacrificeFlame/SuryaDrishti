/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // Enable standalone output for Docker
  
  // Explicitly configure webpack to resolve path aliases
  // Use process.cwd() for Railway/Nixpacks compatibility
  webpack: (config, { dir }) => {
    // Use the dir parameter from Next.js context, or fallback to process.cwd()
    const projectRoot = dir || process.cwd();
    const srcPath = path.resolve(projectRoot, 'src');
    
    // Resolve @ alias to src directory
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': srcPath,
    };
    
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

