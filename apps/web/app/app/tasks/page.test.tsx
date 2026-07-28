import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ApiClientError } from "@/lib/api-client";

const { getCurrentUser, replace } = vi.hoisted(() => ({
  getCurrentUser: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("@/components/app-shell", () => ({
  AppShell: ({ children }: { children: ReactNode }) => <div data-testid="shell">{children}</div>,
}));
vi.mock("@/lib/auth", () => ({ getCurrentUser }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import TasksPage from "./page";

const currentUser = {
  id: "user-1",
  email: "user@example.com",
  display_name: "测试用户",
  is_admin: false,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("TasksPage", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("shows the analysis task queue inside the application shell after authentication", async () => {
    getCurrentUser.mockResolvedValueOnce(currentUser);
    render(<TasksPage />);

    expect(await screen.findByRole("heading", { name: "研究队列" })).toBeInTheDocument();
    expect(screen.getByTestId("shell")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "进入产品空间" })).toHaveAttribute("href", "/app/spaces");
  });

  it("redirects unauthenticated visitors without showing the queue", async () => {
    getCurrentUser.mockRejectedValueOnce(new ApiClientError("UNAUTHORIZED", "登录已失效"));
    render(<TasksPage />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
    expect(screen.queryByRole("heading", { name: "研究队列" })).not.toBeInTheDocument();
  });

  it("shows a Chinese retry state for network errors", async () => {
    const user = userEvent.setup();
    getCurrentUser
      .mockRejectedValueOnce(new ApiClientError("NETWORK_ERROR", "网络请求失败，请稍后重试"))
      .mockResolvedValueOnce(currentUser);
    render(<TasksPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent("网络请求失败，请稍后重试");
    await user.click(screen.getByRole("button", { name: "重试" }));

    expect(await screen.findByRole("heading", { name: "研究队列" })).toBeInTheDocument();
    expect(getCurrentUser).toHaveBeenCalledTimes(2);
  });
});
