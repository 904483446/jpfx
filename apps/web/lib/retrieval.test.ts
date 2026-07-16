import { afterEach, describe, expect, it, vi } from "vitest";

import { apiRequest } from "./api-client";
import { indexDocument, searchSpaceDocuments } from "./retrieval";

vi.mock("./api-client", () => ({ apiRequest: vi.fn() }));

const request = vi.mocked(apiRequest);

describe("retrieval API helpers", () => {
  afterEach(() => vi.clearAllMocks());

  it("indexes one existing document", async () => {
    await indexDocument("document-1");

    expect(request).toHaveBeenCalledWith("/documents/document-1/index", { method: "POST" });
  });

  it("searches within the selected space", async () => {
    await searchSpaceDocuments("space-1", "产品定位", 6);

    expect(request).toHaveBeenCalledWith("/spaces/space-1/retrieval/search", {
      method: "POST",
      body: JSON.stringify({ query: "产品定位", top_k: 6 }),
      headers: { "Content-Type": "application/json" },
    });
  });
});
