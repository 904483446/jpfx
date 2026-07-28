import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("@/components/app-shell", () => ({
  AppShell: ({ children }: { children: ReactNode }) => <div data-testid="shell">{children}</div>,
}));

import TasksPage from "./page";

describe("TasksPage", () => {
  it("places the analysis task queue inside the authenticated application shell", () => {
    render(<TasksPage />);

    expect(screen.getByTestId("shell")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "研究队列" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "进入产品空间" })).toHaveAttribute("href", "/app/spaces");
  });
});
