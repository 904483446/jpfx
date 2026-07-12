import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiClientError, apiRequest, getApiBaseUrl } from "./api-client";

function assertNoContentResponseType(): void {
  // @ts-expect-error 204 responses may be undefined
  const noContentResponse: Promise<{ id: string }> = apiRequest<{ id: string }>("/auth/logout");
  void noContentResponse;
}

void assertNoContentResponseType;

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

  it("maps a rejected network request to a generic ApiClientError", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://127.0.0.1:8000/api/v1");
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connection refused"));

    let rejectedError: unknown;

    try {
      await apiRequest("/health");
    } catch (error) {
      rejectedError = error;
    }

    expect(rejectedError).toBeInstanceOf(ApiClientError);
    expect(rejectedError).toMatchObject({
      code: "NETWORK_ERROR",
      message: "网络请求失败，请稍后重试",
    } satisfies Partial<ApiClientError>);
    expect(rejectedError).not.toHaveProperty("cause");
    expect((rejectedError as ApiClientError).message).not.toContain("connection refused");
  });

  it("returns undefined for a successful empty 204 response", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://127.0.0.1:8000/api/v1");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(null, { status: 204 }));

    await expect(apiRequest<void>("/auth/logout")).resolves.toBeUndefined();
  });
});
