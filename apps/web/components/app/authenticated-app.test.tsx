import { afterEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ApiClientError } from "@/lib/api-client";

const { getCurrentUser, replace } = vi.hoisted(() => ({
  getCurrentUser: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("@/lib/auth", () => ({ getCurrentUser }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import { AuthenticatedApp } from "./authenticated-app";
import { AppShell } from "@/components/app-shell";

describe("AuthenticatedApp", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders the dossier shell navigation and authentication skeleton", async () => {
    let resolveUser: (value: { id: string; email: string; display_name: string; is_admin: boolean; created_at: string; updated_at: string }) => void;
    getCurrentUser.mockImplementationOnce(() => new Promise((resolve) => { resolveUser = resolve; }));
    render(<AppShell><AuthenticatedApp /></AppShell>);

    expect(screen.getByRole("navigation", { name: "主导航" })).toBeInTheDocument();
    expect(screen.getByTestId("context-bar")).toHaveTextContent("工作台");
    expect(screen.getByTestId("auth-loading-skeleton")).toBeInTheDocument();

    await waitFor(() => expect(getCurrentUser).toHaveBeenCalledTimes(1));
    await act(async () => {
      resolveUser!({ id: "user-1", display_name: "测试用户", email: "user@example.com", is_admin: false, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" });
    });
    expect(await screen.findByRole("heading")).toBeInTheDocument();
    expect(await screen.findByText("user@example.com")).toBeInTheDocument();
    expect(screen.queryByTestId("auth-loading-skeleton")).not.toBeInTheDocument();
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

  it("未返回当前用户时显示可重试错误且不跳转", async () => {
    getCurrentUser.mockResolvedValueOnce(undefined);
    render(<AuthenticatedApp />);

    expect(await screen.findByRole("alert")).toHaveTextContent("网络请求失败，请稍后重试");
    expect(screen.getByRole("button", { name: "重试" })).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("卸载后忽略仍在进行的未授权请求", async () => {
    let rejectRequest: (reason: Error) => void;
    getCurrentUser.mockImplementationOnce(() => new Promise((_, reject) => { rejectRequest = reject; }));
    const { unmount } = render(<AuthenticatedApp />);
    await waitFor(() => expect(getCurrentUser).toHaveBeenCalledTimes(1));

    unmount();
    await act(async () => {
      rejectRequest!(new ApiClientError("UNAUTHORIZED", "登录已失效"));
      await Promise.resolve();
    });

    expect(replace).not.toHaveBeenCalled();
  });

  it("连续重试时忽略较早请求的晚到未授权结果", async () => {
    let rejectEarlierRetry: (reason: Error) => void;
    let resolveLatestRetry: (value: { id: string; email: string; display_name: string; is_admin: boolean; created_at: string; updated_at: string }) => void;
    getCurrentUser
      .mockRejectedValueOnce(new ApiClientError("NETWORK_ERROR", "网络请求失败，请稍后重试"))
      .mockImplementationOnce(() => new Promise((_, reject) => { rejectEarlierRetry = reject; }))
      .mockImplementationOnce(() => new Promise((resolve) => { resolveLatestRetry = resolve; }));
    render(<AuthenticatedApp />);

    const retry = await screen.findByRole("button", { name: "重试" });
    await act(async () => {
      retry.click();
      retry.click();
    });
    await waitFor(() => expect(getCurrentUser).toHaveBeenCalledTimes(3));
    await act(async () => {
      resolveLatestRetry!({ id: "user-1", display_name: "测试用户", email: "user@example.com", is_admin: false, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" });
      await Promise.resolve();
    });

    expect(await screen.findByRole("heading", { name: "欢迎回来，测试用户" })).toBeInTheDocument();
    await act(async () => {
      rejectEarlierRetry!(new ApiClientError("UNAUTHORIZED", "登录已失效"));
      await Promise.resolve();
    });
    expect(screen.getByRole("heading", { name: "欢迎回来，测试用户" })).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
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
