import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiClientError, apiRequest, getApiBaseUrl } from "./api-client";

describe("getApiBaseUrl", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("throws a Chinese configuration error when the API base URL is missing", () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "   ");

    expect(() => getApiBaseUrl()).toThrow("缺少 NEXT_PUBLIC_API_BASE_URL 配置");
  });
});

describe("apiRequest", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
  });

  it("normalizes the URL and always includes credentials", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", " http://localhost:8000/ ");
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }));

    await expect(apiRequest<{ ok: boolean }>("/api/v1/auth/me")).resolves.toEqual({
      ok: true,
    });
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/auth/me", {
      credentials: "include",
    });
  });

  it("maps the backend Chinese error structure to ApiClientError", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: "UNAUTHORIZED",
            message: "登录状态无效或已过期",
            details: {},
          },
        }),
        { status: 401 },
      ),
    );

    await expect(apiRequest("/api/v1/auth/me")).rejects.toMatchObject({
      code: "UNAUTHORIZED",
      message: "登录状态无效或已过期",
      details: {},
    } satisfies Partial<ApiClientError>);
  });
});
