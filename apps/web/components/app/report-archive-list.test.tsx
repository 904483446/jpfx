import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ApiClientError } from "@/lib/api-client";

const { listReports, replace } = vi.hoisted(() => ({ listReports: vi.fn(), replace: vi.fn() }));
vi.mock("@/lib/reports", () => ({ listReports }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import { ReportArchiveList } from "./report-archive-list";

const report = {
  id: "report-1", space_id: "space-1", task_id: "task-1", title: "企业知识库 Copilot 竞品报告", version: 1,
  created_at: "2026-07-17T00:00:00Z", updated_at: "2026-07-17T00:00:00Z", structured_json: {},
};

describe("ReportArchiveList", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("links each real report to its existing dossier page", async () => {
    listReports.mockResolvedValue([report]);
    render(<ReportArchiveList />);

    expect(await screen.findByRole("link", { name: report.title })).toHaveAttribute("href", "/app/reports/report-1");
  });

  it("shows an explicit empty state when no report is archived", async () => {
    listReports.mockResolvedValue([]);
    render(<ReportArchiveList />);

    expect(await screen.findByText("还没有归档报告")).toBeInTheDocument();
  });

  it("retries a non-authentication loading failure", async () => {
    const user = userEvent.setup();
    listReports.mockRejectedValueOnce(new ApiClientError("NETWORK_ERROR", "报告暂时不可用")).mockResolvedValueOnce([report]);
    render(<ReportArchiveList />);

    expect(await screen.findByRole("alert")).toHaveTextContent("报告暂时不可用");
    await user.click(screen.getByRole("button", { name: "重试" }));
    expect(await screen.findByRole("link", { name: report.title })).toBeInTheDocument();
  });

  it("redirects to login when the archive request is unauthorized", async () => {
    listReports.mockRejectedValue(new ApiClientError("UNAUTHORIZED", "登录已过期"));
    render(<ReportArchiveList />);

    await vi.waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});
