import { afterEach, describe, expect, it, vi } from "vitest";

import { getApiProxyRewrites } from "./next.config";

describe("getApiProxyRewrites", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("returns no rewrites when API_PROXY_TARGET is empty", () => {
    vi.stubEnv("API_PROXY_TARGET", "");

    expect(getApiProxyRewrites()).toEqual([]);
  });

  it("returns no rewrites when API_PROXY_TARGET is whitespace", () => {
    vi.stubEnv("API_PROXY_TARGET", "   ");

    expect(getApiProxyRewrites()).toEqual([]);
  });

  it("proxies API requests to a target without its trailing slash", () => {
    vi.stubEnv("API_PROXY_TARGET", "https://jpfx-api.up.railway.app///");

    expect(getApiProxyRewrites()).toEqual([
      {
        source: "/api/:path*",
        destination: "https://jpfx-api.up.railway.app/api/:path*",
      },
    ]);
  });
});
