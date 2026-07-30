import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "./page";

describe("Home workflow preview", () => {
  it("explains that the research flow keeps evidence traceable", () => {
    render(<Home />);

    const preview = screen.getByRole("region", { name: "产品流程预览" });
    expect(within(preview).getByText("研究流程")).toBeInTheDocument();
    expect(within(preview).getByText("每一步都保留可核查的来源与研究记录。")).toBeInTheDocument();
  });
});
