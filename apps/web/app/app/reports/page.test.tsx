import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("@/components/app-shell", () => ({
  AppShell: ({ children }: { children: ReactNode }) => <div data-testid="shell">{children}</div>,
}));
vi.mock("@/components/app/report-archive-list", () => ({
  ReportArchiveList: () => <div>archive list</div>,
}));

import ReportsPage from "./page";

describe("ReportsPage", () => {
  it("places the report center inside the authenticated application shell", () => {
    render(<ReportsPage />);

    expect(screen.getByTestId("shell")).toHaveTextContent("报告中心");
    expect(screen.getByRole("heading", { name: "研究归档" })).toBeInTheDocument();
    expect(screen.getByText("archive list")).toBeInTheDocument();
  });
});
