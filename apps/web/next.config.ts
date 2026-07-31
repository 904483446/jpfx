import type { NextConfig } from "next";

export function getApiProxyRewrites() {
  const target = process.env.API_PROXY_TARGET?.trim().replace(/\/+$/, "");

  if (!target) {
    return [];
  }

  return [
    {
      source: "/api/:path*",
      destination: `${target}/api/:path*`,
    },
  ];
}

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1", "localhost"],
  async rewrites() {
    return getApiProxyRewrites();
  },
};

export default nextConfig;
