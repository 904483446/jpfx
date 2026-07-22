import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const { getAnalysisTask, retryAnalysisTask, replace } = vi.hoisted(() => ({ getAnalysisTask: vi.fn(), retryAnalysisTask: vi.fn(), replace: vi.fn() }));
vi.mock("@/lib/analysis-tasks", () => ({ getAnalysisTask, retryAnalysisTask }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));
import { AnalysisTaskStatus } from "./analysis-task-status";

const failedTask = { id: "task-1", space_id: "space-1", title: "写作助手", industry: "AI", product_direction: "写作", keywords: [], known_competitors: [], discovery_mode: "semi_auto", status: "failed", stage: "模型调用失败", completed_at: null, final_competitors: ["Example AI"], candidates: [] };

describe("AnalysisTaskStatus", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); vi.useRealTimers(); });

  it("stops polling after a completed task", async () => {
    vi.useFakeTimers(); getAnalysisTask.mockResolvedValue({ ...failedTask, status: "completed", stage: "报告已生成" });
    render(<AnalysisTaskStatus taskId="task-1" />);
    await vi.advanceTimersByTimeAsync(0);
    expect(getAnalysisTask).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(6000);
    expect(getAnalysisTask).toHaveBeenCalledTimes(1);
  });

  it("retries a failed task once while disabling duplicate submission", async () => {
    const interaction = userEvent.setup(); getAnalysisTask.mockResolvedValueOnce(failedTask); retryAnalysisTask.mockImplementationOnce(() => new Promise(() => {}));
    render(<AnalysisTaskStatus taskId="task-1" />);
    const retry = await screen.findByRole("button", { name: "重新分析" });
    await interaction.click(retry);
    expect(retry).toBeDisabled(); expect(retryAnalysisTask).toHaveBeenCalledWith("task-1");
  });

  it("renders a Chinese stage timeline from the task status and failure stage", async () => {
    getAnalysisTask.mockResolvedValueOnce(failedTask);
    render(<AnalysisTaskStatus taskId="task-1" />);
    expect(await screen.findByText("分析进度")).toBeInTheDocument();
    expect(screen.getByText("模型调用失败")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "重新分析" })).toBeInTheDocument();
  });
});
