/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // Enable standalone output for Docker
  // Next.js automatically resolves path aliases from tsconfig.json
  // No custom webpack config needed - Next.js handles it natively
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

