import { afterEach, describe, expect, it, vi } from "vitest";

import { apiRequest } from "./api-client";
import { getCurrentUser, login, logout, register } from "./auth";

vi.mock("./api-client", () => ({
  apiRequest: vi.fn(),
}));

const apiRequestMock = vi.mocked(apiRequest);

describe("auth API helpers", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("register delegates the mapped JSON request to the registration endpoint", async () => {
    const input = {
      email: "ada@example.com",
      password: "secure-password",
      displayName: "Ada Lovelace",
    };

    await register(input);

    expect(apiRequestMock).toHaveBeenCalledWith("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: input.email,
        password: input.password,
        display_name: input.displayName,
      }),
    });
  });

  it("login delegates a JSON request to the login endpoint", async () => {
    const input = { email: "ada@example.com", password: "secure-password" };

    await login(input);

    expect(apiRequestMock).toHaveBeenCalledWith("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
  });

  it("getCurrentUser delegates to the current-user endpoint", async () => {
    await getCurrentUser();

    expect(apiRequestMock).toHaveBeenCalledWith("/auth/me");
  });

  it("logout delegates a POST request to the logout endpoint", async () => {
    await logout();

    expect(apiRequestMock).toHaveBeenCalledWith("/auth/logout", { method: "POST" });
  });
});
