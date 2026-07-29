import { afterEach, describe, expect, it } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { AnalysisAgentRunHistory } from "./analysis-agent-run-history";

describe("AnalysisAgentRunHistory", () => {
  afterEach(cleanup);

  it("renders the latest attempt with Chinese labels and a safe failure reason", () => {
    render(
      <AnalysisAgentRunHistory
        agentRuns={[
          { attempt: 2, agent_key: "evidence_collection", status: "completed", started_at: "2026-07-29T08:00:00Z", completed_at: "2026-07-29T08:01:00Z", failure_reason: null },
          { attempt: 2, agent_key: "quality_check", status: "failed", started_at: "2026-07-29T08:01:00Z", completed_at: "2026-07-29T08:01:30Z", failure_reason: "证据质量不足，请补充公开来源后重试" },
          { attempt: 2, agent_key: "model_analysis", status: "skipped", started_at: null, completed_at: "2026-07-29T08:01:30Z", failure_reason: null },
          { attempt: 2, agent_key: "report_generation", status: "skipped", started_at: null, completed_at: "2026-07-29T08:01:30Z", failure_reason: null },
          { attempt: 1, agent_key: "evidence_collection", status: "completed", started_at: "2026-07-29T07:00:00Z", completed_at: "2026-07-29T07:01:00Z", failure_reason: null },
        ]}
      />,
    );

    expect(screen.getByText("第 2 次运行")).toBeInTheDocument();
    expect(screen.getAllByText("证据收集")).toHaveLength(2);
    expect(screen.getByText("质量检查")).toBeInTheDocument();
    expect(screen.getByText("模型分析")).toBeInTheDocument();
    expect(screen.getAllByText("未执行")).toHaveLength(2);
    expect(screen.getByText("证据质量不足，请补充公开来源后重试")).toBeInTheDocument();
    expect(screen.queryByText("quality_check")).not.toBeInTheDocument();
    expect(screen.queryByText("skipped")).not.toBeInTheDocument();
  });

  it("orders attempts from newest to oldest", () => {
    render(
      <AnalysisAgentRunHistory
        agentRuns={[
          { attempt: 1, agent_key: "evidence_collection", status: "completed", started_at: null, completed_at: null, failure_reason: null },
          { attempt: 2, agent_key: "evidence_collection", status: "running", started_at: null, completed_at: null, failure_reason: null },
        ]}
      />,
    );

    expect(screen.getAllByText(/第 \d+ 次运行/).map((item) => item.textContent)).toEqual(["第 2 次运行", "第 1 次运行"]);
  });
});
