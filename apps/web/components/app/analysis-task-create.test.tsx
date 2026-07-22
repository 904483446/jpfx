import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const { createAnalysisTask, replace } = vi.hoisted(() => ({ createAnalysisTask: vi.fn(), replace: vi.fn() }));
vi.mock("@/lib/analysis-tasks", () => ({ createAnalysisTask }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));
import { AnalysisTaskCreate } from "./analysis-task-create";

describe("AnalysisTaskCreate", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("creates a task without any known competitor", async () => {
    const interaction = userEvent.setup(); createAnalysisTask.mockResolvedValueOnce({ id: "task-1" });
    render(<AnalysisTaskCreate spaceId="space-1" />);
    await interaction.type(screen.getByLabelText("任务名称"), "写作助手");
    await interaction.type(screen.getByLabelText("所属行业"), "AI");
    await interaction.type(screen.getByLabelText("产品方向"), "写作");
    await interaction.click(screen.getByRole("button", { name: "创建并发现候选" }));
    await waitFor(() => expect(createAnalysisTask).toHaveBeenCalledWith("space-1", expect.objectContaining({ knownCompetitors: [] })));
    expect(replace).toHaveBeenCalledWith("/app/tasks/task-1");
  });

  it("presents the task form as an analysis dossier", () => {
    render(<AnalysisTaskCreate spaceId="space-1" />);
    expect(screen.getByText("分析档案")).toBeInTheDocument();
    expect(screen.getByText("已知竞品（可选，最多 3 个）")).toBeInTheDocument();
  });
});
