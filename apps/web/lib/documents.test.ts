import { afterEach, describe, expect, it, vi } from "vitest";

import { apiRequest } from "./api-client";
import { deleteDocument, listDocuments, uploadDocument } from "./documents";

vi.mock("./api-client", () => ({ apiRequest: vi.fn() }));

const request = vi.mocked(apiRequest);

describe("documents API helpers", () => {
  afterEach(() => vi.clearAllMocks());

  it("lists documents in a space", async () => {
    await listDocuments("space-1");

    expect(request).toHaveBeenCalledWith("/spaces/space-1/documents");
  });

  it("uploads one file as multipart form data", async () => {
    const file = new File(["content"], "brief.txt", { type: "text/plain" });

    await uploadDocument("space-1", file);

    expect(request).toHaveBeenCalledWith(
      "/spaces/space-1/documents",
      expect.objectContaining({ method: "POST" }),
    );
    const [, init] = request.mock.calls[0];
    expect(init?.body).toBeInstanceOf(FormData);
    expect((init?.body as FormData).get("file")).toBe(file);
    expect(init?.headers).toBeUndefined();
  });

  it("deletes one document", async () => {
    await deleteDocument("document-1");

    expect(request).toHaveBeenCalledWith("/documents/document-1", {
      method: "DELETE",
    });
  });
});
