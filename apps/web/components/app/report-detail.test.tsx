import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ApiClientError } from "@/lib/api-client";

const { getReport, getReportEvidence, downloadReport, replace } = vi.hoisted(() => ({
  getReport: vi.fn(), getReportEvidence: vi.fn(), downloadReport: vi.fn(), replace: vi.fn(),
}));
vi.mock("@/lib/reports", () => ({ getReport, getReportEvidence, downloadReport }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import { ReportDetail } from "./report-detail";

const report = {
  id: "report-1", space_id: "space-1", task_id: "task-1", title: "企业知识库 Copilot 竞品报告", version: 1,
  created_at: "2026-07-17T00:00:00Z", updated_at: "2026-07-17T00:00:00Z",
  structured_json: {
    executive_summary: "公开网页与内部资料共同支持此结论。",
    competitors: [{ name: "竞品 A", positioning: "知识库助手", core_features: ["检索", "引用"], strengths: ["配置快"], weaknesses: ["定制有限"], differentiation_opportunities: ["中文工作流"], recommendations: ["优先展示引用"], risks: ["公开信息可能变化"] }],
  },
};
const evidence = [
  { id: "e1", source_type: "web", source_title: "官网", source_url: "https://example.com", quote: "公开功能说明", retrieved_at: "2026-07-17T00:00:00Z" },
  { id: "e2", source_type: "private_knowledge", source_title: "内部访谈", source_url: null, quote: "用户反馈", retrieved_at: null },
  { id: "e3", source_type: "model_inference", source_title: "模型推断", source_url: null, quote: "需要验证", retrieved_at: null },
];

describe("ReportDetail", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("renders structured competitor analysis alongside an independent evidence ledger", async () => {
    getReport.mockResolvedValue(report); getReportEvidence.mockResolvedValue(evidence);
    render(<ReportDetail reportId="report-1" />);

    expect(await screen.findByRole("heading", { name: report.title })).toBeInTheDocument();
    expect(screen.getByText("竞品 A")).toBeInTheDocument();
    expect(screen.getByText("产品建议")).toBeInTheDocument();
    expect(screen.getByText("风险与不确定性")).toBeInTheDocument();
    expect(screen.getByText("公开网页")).toBeInTheDocument();
    expect(screen.getByText("私有知识库")).toBeInTheDocument();
    expect(screen.getAllByText("模型推断").length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: "官网" })).toHaveAttribute("href", "https://example.com");
    expect(screen.getByText("模型推断不构成事实证据，需进一步验证。")).toBeInTheDocument();
  });

  it("downloads the selected export format", async () => {
    const user = userEvent.setup(); getReport.mockResolvedValue(report); getReportEvidence.mockResolvedValue(evidence);
    render(<ReportDetail reportId="report-1" />);
    await screen.findByRole("heading", { name: report.title });
    await user.click(screen.getByRole("button", { name: "下载 PDF" }));
    expect(downloadReport).toHaveBeenCalledWith("report-1", "pdf");
  });

  it.each(["javascript:alert(1)", "file:///etc/passwd", "data:text/html,unsafe"])("renders unsafe evidence URL %s as plain text instead of a link", async (unsafeUrl) => {
    getReport.mockResolvedValue(report);
    getReportEvidence.mockResolvedValue([...evidence, { id: "e4", source_type: "web", source_title: "不安全来源", source_url: unsafeUrl, quote: null, retrieved_at: null }]);
    render(<ReportDetail reportId="report-1" />);

    expect(await screen.findByText("不安全来源")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "不安全来源" })).not.toBeInTheDocument();
  });

  it("redirects to login when the report is unauthorized", async () => {
    getReport.mockRejectedValue(new ApiClientError("UNAUTHORIZED", "登录已过期"));
    render(<ReportDetail reportId="report-1" />);
    await screen.findByText("正在加载报告…");
    await vi.waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});
