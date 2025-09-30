/** @type {import('next').NextConfig} */
const nextConfig = {
  // Comment out basePath for local development
  basePath: '/amc_chatbot',
  reactStrictMode: true,
  trailingSlash: true,
  swcMinify: true,
  // Required for static export
  images: {
    unoptimized: true
  },
  // Production optimizations
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },
  // Compiler optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  generateEtags: false,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'https://jbs-ai.com/amc_api/:path*' // Production API proxy
          : 'http://localhost:8022/:path*', // Local development API proxy
      },
    ]
  },
}

module.exports = nextConfig
