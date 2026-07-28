import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("@/components/app-shell", () => ({
  AppShell: ({ children }: { children: ReactNode }) => <div data-testid="shell">{children}</div>,
}));
vi.mock("@/components/app/authenticated-app", () => ({
  AuthenticatedApp: () => <div>已加载产品空间</div>,
}));

import SpacesPage from "./page";

describe("SpacesPage", () => {
  it("places the product spaces inside the application shell", () => {
    render(<SpacesPage />);

    expect(screen.getByTestId("shell")).toHaveTextContent("已加载产品空间");
  });
});
