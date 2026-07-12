type ErrorDetails = Record<string, unknown>;

export class ApiClientError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly details: ErrorDetails = {},
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

export function getApiBaseUrl(): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

  if (!baseUrl) {
    throw new Error("缺少 NEXT_PUBLIC_API_BASE_URL 配置");
  }

  return baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  try {
    const normalizedPath = path.startsWith("/") ? path.slice(1) : path;
    const response = await fetch(`${getApiBaseUrl()}/${normalizedPath}`, {
      ...init,
      credentials: "include",
    });

    if (response.status === 204) {
      return undefined as T;
    }

    const body = await parseJson(response);

    if (!response.ok) {
      const error = getBackendError(body);

      if (error) {
        throw new ApiClientError(error.code, error.message, error.details);
      }

      throw new ApiClientError("NETWORK_ERROR", "网络请求失败，请稍后重试");
    }

    return body as T;
  } catch (error) {
    if (error instanceof ApiClientError || error instanceof Error && error.message === "缺少 NEXT_PUBLIC_API_BASE_URL 配置") {
      throw error;
    }

    throw new ApiClientError("NETWORK_ERROR", "网络请求失败，请稍后重试");
  }
}

async function parseJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function getBackendError(
  body: unknown,
): { code: string; message: string; details: ErrorDetails } | null {
  if (!isRecord(body) || !isRecord(body.error)) {
    return null;
  }

  const { code, message, details } = body.error;

  if (typeof code !== "string" || typeof message !== "string" || !isRecord(details)) {
    return null;
  }

  return { code, message, details };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
