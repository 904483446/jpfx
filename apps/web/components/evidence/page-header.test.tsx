import { afterEach, describe, expect, it } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { PageHeader } from "./page-header";

describe("PageHeader", () => {
  afterEach(cleanup);

  it("renders the eyebrow, title, description, and actions passed to it", () => {
    render(
      <PageHeader
        actions={<button type="button">新建文档</button>}
        description="将可追溯的材料集中在一个工作台中。"
        eyebrow="证据工作台"
        title="项目证据"
      />,
    );

    expect(screen.getByText("证据工作台")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "项目证据" })).toBeInTheDocument();
    expect(screen.getByText("将可追溯的材料集中在一个工作台中。")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "新建文档" })).toBeInTheDocument();
  });
});
