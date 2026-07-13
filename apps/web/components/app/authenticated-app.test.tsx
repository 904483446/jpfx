import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ApiClientError } from "@/lib/api-client";

const { getCurrentUser, replace } = vi.hoisted(() => ({
  getCurrentUser: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("@/lib/auth", () => ({ getCurrentUser }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import { AuthenticatedApp } from "./authenticated-app";

describe("AuthenticatedApp", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("验证完成后显示当前用户信息", async () => {
    let resolveUser: (value: { id: string; email: string; display_name: string; is_admin: boolean; created_at: string; updated_at: string }) => void;
    getCurrentUser.mockImplementationOnce(() => new Promise((resolve) => { resolveUser = resolve; }));
    render(<AuthenticatedApp />);

    expect(screen.getByText("正在验证登录状态…")).toBeInTheDocument();
    await waitFor(() => expect(getCurrentUser).toHaveBeenCalledTimes(1));
    resolveUser!({ id: "user-1", display_name: "测试用户", email: "user@example.com", is_admin: false, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" });

    expect(await screen.findByRole("heading", { name: "欢迎回来，测试用户" })).toBeInTheDocument();
    expect(screen.getByText("user@example.com")).toBeInTheDocument();
  });

  it("未授权时仅跳转到登录页", async () => {
    getCurrentUser.mockRejectedValueOnce(new ApiClientError("UNAUTHORIZED", "登录已失效"));
    render(<AuthenticatedApp />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
    expect(replace).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("网络错误显示重试操作且不跳转", async () => {
    const user = userEvent.setup();
    getCurrentUser
      .mockRejectedValueOnce(new ApiClientError("NETWORK_ERROR", "网络请求失败，请稍后重试"))
      .mockResolvedValueOnce({ id: "user-1", display_name: "测试用户", email: "user@example.com", is_admin: false, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" });
    render(<AuthenticatedApp />);

    expect(await screen.findByRole("alert")).toHaveTextContent("网络请求失败，请稍后重试");
    expect(replace).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "重试" }));

    expect(await screen.findByRole("heading", { name: "欢迎回来，测试用户" })).toBeInTheDocument();
    expect(getCurrentUser).toHaveBeenCalledTimes(2);
    expect(replace).not.toHaveBeenCalled();
  });
});
