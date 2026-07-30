import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AppShell } from "./app-shell";

vi.mock("next/navigation", () => ({
  usePathname: () => "/app/settings",
  useRouter: () => ({ replace: vi.fn() }),
}));

describe("AppShell navigation", () => {
  it("marks the current settings page in the primary navigation", () => {
    render(<AppShell><h1>模型设置</h1></AppShell>);

    const navigation = screen.getByRole("navigation", { name: "主导航" });

    expect(within(navigation).getByRole("link", { name: /^设置/ })).toHaveAttribute("aria-current", "page");
  });
});
