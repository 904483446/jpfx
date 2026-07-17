import { afterEach, describe, expect, it, vi } from "vitest";

import { apiRequest } from "./api-client";
import { getDeepSeekConfig, saveDeepSeekConfig } from "./model-configs";

vi.mock("./api-client", () => ({ apiRequest: vi.fn() }));

const request = vi.mocked(apiRequest);

describe("DeepSeek configuration API helpers", () => {
  afterEach(() => vi.clearAllMocks());

  it("loads the safe DeepSeek configuration summary", async () => {
    await getDeepSeekConfig();

    expect(request).toHaveBeenCalledWith("/model-configs/deepseek");
  });

  it("submits a key without retaining it in the client helper", async () => {
    await saveDeepSeekConfig("sk-secret");

    expect(request).toHaveBeenCalledWith("/model-configs/deepseek", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: "sk-secret" }),
    });
  });
});
