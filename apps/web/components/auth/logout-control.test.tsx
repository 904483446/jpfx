import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const { logout, replace } = vi.hoisted(() => ({
  logout: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("@/lib/auth", () => ({ logout }));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

import { LogoutControl } from "./logout-control";

describe("LogoutControl", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("calls logout and redirects to login after success", async () => {
    const user = userEvent.setup();
    logout.mockResolvedValueOnce(undefined);
    render(<LogoutControl />);

    await user.click(screen.getByRole("button", { name: "退出登录" }));

    await waitFor(() => expect(logout).toHaveBeenCalledTimes(1));
    expect(replace).toHaveBeenCalledWith("/login");
  });

  it("shows a disabled pending state and ignores repeat clicks", async () => {
    const user = userEvent.setup();
    let resolveLogout: () => void = () => undefined;
    logout.mockImplementationOnce(() => new Promise<void>((resolve) => { resolveLogout = resolve; }));
    render(<LogoutControl />);

    const button = screen.getByRole("button", { name: "退出登录" });
    await user.click(button);

    expect(button).toHaveTextContent("退出中…");
    expect(button).toBeDisabled();
    await user.click(button);
    expect(logout).toHaveBeenCalledTimes(1);

    resolveLogout();
  });

  it("shows an error and restores the button when logout fails", async () => {
    const user = userEvent.setup();
    logout.mockRejectedValueOnce(new Error("network unavailable"));
    render(<LogoutControl />);

    const button = screen.getByRole("button", { name: "退出登录" });
    await user.click(button);

    expect(await screen.findByRole("alert")).toHaveTextContent("退出失败，请稍后重试");
    expect(button).toHaveTextContent("退出登录");
    expect(button).not.toBeDisabled();
    expect(replace).not.toHaveBeenCalled();
  });
});
