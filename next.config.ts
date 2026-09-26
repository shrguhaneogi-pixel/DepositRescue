import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["framer-motion"],
  async rewrites() {
    return [
      {
        source: "/api/py/:path*",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8000/api/py/:path*"
            : "/api/py/:path*",
      },
      {
        source: "/api/audit",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8000/api/audit"
            : "/api/audit",
      },
    ];
  },
};

export default nextConfig;
