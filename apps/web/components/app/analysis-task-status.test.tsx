import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const { getAnalysisTask, retryAnalysisTask, replace } = vi.hoisted(() => ({ getAnalysisTask: vi.fn(), retryAnalysisTask: vi.fn(), replace: vi.fn() }));
vi.mock("@/lib/analysis-tasks", () => ({ getAnalysisTask, retryAnalysisTask }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));
import { AnalysisTaskStatus } from "./analysis-task-status";

const failedTask = { id: "task-1", space_id: "space-1", title: "写作助手", industry: "AI", product_direction: "写作", keywords: [], known_competitors: [], discovery_mode: "semi_auto", status: "failed", stage: "模型调用失败", completed_at: null, final_competitors: ["Example AI"], candidates: [], agent_runs: [] };

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

  it("renders neutral Chinese failure copy without attributing the failure to model invocation", async () => {
    getAnalysisTask.mockResolvedValueOnce(failedTask);
    render(<AnalysisTaskStatus taskId="task-1" />);
    expect(await screen.findByText("分析进度")).toBeInTheDocument();
    expect(screen.getByText("任务未完成，请重试")).toBeInTheDocument();
    expect(screen.queryByText("模型调用失败")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "重新分析" })).toBeInTheDocument();
  });

  it("uses Chinese labels for queued and completed task statuses", async () => {
    getAnalysisTask.mockResolvedValueOnce({ ...failedTask, status: "queued", stage: null });
    const { unmount } = render(<AnalysisTaskStatus taskId="task-1" />);
    expect(await screen.findByText("等待执行")).toBeInTheDocument();
    unmount();

    getAnalysisTask.mockResolvedValueOnce({ ...failedTask, status: "completed", stage: null });
    render(<AnalysisTaskStatus taskId="task-1" />);
    expect(await screen.findByText("已完成")).toBeInTheDocument();
  });

  it("does not highlight a speculative timeline stage for failed tasks", async () => {
    getAnalysisTask.mockResolvedValueOnce(failedTask);
    render(<AnalysisTaskStatus taskId="task-1" />);
    await screen.findByText("分析进度");
    expect(screen.getByText("模型调用")).not.toHaveClass("font-medium");
  });

  it("shows evidence quality checking as a distinct running stage", async () => {
    getAnalysisTask.mockResolvedValueOnce({ ...failedTask, status: "running", stage: "quality_checking" });
    render(<AnalysisTaskStatus taskId="task-1" />);

    expect(await screen.findAllByText("证据质量检查")).not.toHaveLength(0);
    expect(screen.queryByText("quality_checking")).not.toBeInTheDocument();
  });

  it("shows the agent run history returned with the task", async () => {
    getAnalysisTask.mockResolvedValueOnce({ ...failedTask, agent_runs: [{ attempt: 1, agent_key: "quality_check", status: "failed", started_at: null, completed_at: null, failure_reason: "证据质量不足，请补充公开来源后重试" }] });
    render(<AnalysisTaskStatus taskId="task-1" />);

    expect(await screen.findByText("Agent 运行记录")).toBeInTheDocument();
    expect(screen.getByText("证据质量不足，请补充公开来源后重试")).toBeInTheDocument();
  });

  it.each([
    ["retrieving_private_knowledge", "私有知识检索", "证据采集"],
    ["analyzing", "正在模型分析", "模型调用"],
  ])("maps backend stage %s to a Chinese label at the correct timeline position", async (stage, label, activeTimelineStage) => {
    getAnalysisTask.mockResolvedValueOnce({ ...failedTask, status: stage === "failed" ? "failed" : "running", stage });
    render(<AnalysisTaskStatus taskId="task-1" />);

    expect(await screen.findAllByText(label)).not.toHaveLength(0);
    expect(screen.getByText(activeTimelineStage)).toHaveClass("font-medium");
    expect(screen.queryByText(stage)).not.toBeInTheDocument();
  });
});
