import { afterEach, describe, expect, it } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { StatusStamp } from "./status-stamp";

describe("StatusStamp", () => {
  afterEach(cleanup);

  it("renders the indexed Chinese label with an accessible status name", () => {
    render(<StatusStamp status="indexed" />);

    expect(screen.getByText("已索引")).toBeInTheDocument();
    expect(screen.getByLabelText("文档状态：已索引")).toBeInTheDocument();
  });
});
