import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["framer-motion"],
  async rewrites() {
    return [
      {
        source: "/api/py/:path*",
        destination: "/api/:path*",
      },
    ];
  },
};

export default nextConfig;
