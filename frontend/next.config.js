/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // Enable standalone output for Docker
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') + '/api/:path*' || 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig

