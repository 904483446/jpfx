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

  it("normalizes the API base URL and relative path while always including credentials", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", " http://127.0.0.1:8000/api/v1/ ");
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }));

    await expect(apiRequest<{ ok: boolean }>("/auth/me")).resolves.toEqual({
      ok: true,
    });
    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/api/v1/auth/me", {
      credentials: "include",
    });
  });

  it("maps the backend Chinese error structure to ApiClientError", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://127.0.0.1:8000/api/v1/");
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

    await expect(apiRequest("/auth/me")).rejects.toMatchObject({
      code: "UNAUTHORIZED",
      message: "登录状态无效或已过期",
      details: {},
    } satisfies Partial<ApiClientError>);
  });
});
