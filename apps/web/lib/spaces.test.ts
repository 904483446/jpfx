import { afterEach, describe, expect, it, vi } from "vitest";

import { apiRequest } from "./api-client";
import { createSpace, listSpaces } from "./spaces";

vi.mock("./api-client", () => ({ apiRequest: vi.fn() }));

const request = vi.mocked(apiRequest);

describe("spaces API helpers", () => {
  afterEach(() => vi.clearAllMocks());

  it("lists the current user's spaces", async () => {
    await listSpaces();

    expect(request).toHaveBeenCalledWith("/spaces");
  });

  it("maps all supported fields", async () => {
    await createSpace({
      name: " 企业知识库 Copilot ",
      industry: "企业服务",
      productDirection: "AI 知识库",
      description: "面向内部知识问答",
    });

    expect(request).toHaveBeenCalledWith("/spaces", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "企业知识库 Copilot",
        industry: "企业服务",
        product_direction: "AI 知识库",
        description: "面向内部知识问答",
      }),
    });
  });

  it("omits blank optional fields", async () => {
    await createSpace({ name: " 空间 ", industry: " ", productDirection: "", description: "\n" });

    expect(request).toHaveBeenCalledWith("/spaces", expect.objectContaining({
      body: JSON.stringify({ name: "空间" }),
    }));
  });
});
