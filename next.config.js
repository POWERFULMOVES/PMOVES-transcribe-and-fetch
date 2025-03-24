/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    forceSwcTransforms: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/:path*',
      },
    ]
  },
  images: {
    domains: ['i.ytimg.com', 'img.youtube.com'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'i.ytimg.com',
      },
      {
        protocol: 'https',
        hostname: 'img.youtube.com',
      }
    ]
  }
}

module.exports = nextConfig