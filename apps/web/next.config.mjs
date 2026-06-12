/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@game-health/types"],
  output: process.env.GITHUB_PAGES === "true" ? "export" : undefined,
};

export default nextConfig;
