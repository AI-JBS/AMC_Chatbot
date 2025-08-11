/** @type {import('next').NextConfig} */
const nextConfig = {
  basePath: '/amc_chatbot',
  reactStrictMode: true,
  trailingSlash: true,
  swcMinify: true,
  output: 'standalone',
  // Production optimizations
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },
  // Compiler optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // Static file serving
  trailingSlash: false,
  generateEtags: false,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://jbs-ai.com/amc_api/:path*', // Production API proxy
      },
    ]
  },
}

module.exports = nextConfig
