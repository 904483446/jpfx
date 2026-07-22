import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AppShell } from "./app-shell";

describe("AppShell", () => {
  it("exposes the primary navigation and keeps page content in the main landmark", () => {
    render(<AppShell><h1>空间总览</h1></AppShell>);

    expect(screen.getByRole("navigation", { name: "主导航" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /产品空间/ })).toHaveAttribute("href", "/app/spaces");
    expect(screen.getByRole("main", { name: "主内容" })).toContainElement(screen.getByRole("heading", { name: "空间总览" }));
  });
});
