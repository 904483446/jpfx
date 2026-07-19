import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "./page";

describe("Home", () => {
  it("提供登录、创建账户入口和清晰的价值主张", () => {
    render(<Home />);

    expect(
      screen.getAllByRole("link", { name: "登录" }).some((link) => link.getAttribute("href") === "/login"),
    ).toBe(true);
    expect(
      screen.getAllByRole("link", { name: "创建账户" }).some((link) => link.getAttribute("href") === "/register"),
    ).toBe(true);
    expect(
      screen.getByRole("heading", { level: 1, name: "把竞品洞察变成可验证的决策。" }),
    ).toBeInTheDocument();
  });
});
