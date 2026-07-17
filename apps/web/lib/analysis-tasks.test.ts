import { describe, expect, it, vi } from "vitest";

const { apiRequest } = vi.hoisted(() => ({ apiRequest: vi.fn() }));
vi.mock("./api-client", () => ({ apiRequest }));

import { autoSelectCompetitors, createAnalysisTask, selectCompetitors } from "./analysis-tasks";

describe("analysis task API client", () => {
  it("creates a task with zero known competitors", async () => {
    apiRequest.mockResolvedValueOnce({ id: "task-1" });

    await createAnalysisTask("space-1", {
      title: "AI 写作竞品分析", industry: "AI", productDirection: "写作", keywords: ["协作"], knownCompetitors: [], discoveryMode: "semi_auto",
    });

    expect(apiRequest).toHaveBeenCalledWith("/spaces/space-1/analysis-tasks", expect.objectContaining({
      method: "POST", body: JSON.stringify({ title: "AI 写作竞品分析", industry: "AI", product_direction: "写作", keywords: ["协作"], known_competitors: [], discovery_mode: "semi_auto" }),
    }));
  });

  it("selects one to three candidates and auto-selects evidenced candidates", async () => {
    apiRequest.mockClear();
    await selectCompetitors("task-1", ["candidate-1"]);
    await autoSelectCompetitors("task-1");

    expect(apiRequest).toHaveBeenNthCalledWith(1, "/analysis-tasks/task-1/competitors", expect.objectContaining({ method: "PUT", body: JSON.stringify({ candidate_ids: ["candidate-1"] }) }));
    expect(apiRequest).toHaveBeenNthCalledWith(2, "/analysis-tasks/task-1/competitors/auto-select", expect.objectContaining({ method: "POST" }));
  });
});
