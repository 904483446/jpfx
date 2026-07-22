import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const { getAnalysisTask, autoSelectCompetitors, selectCompetitors, replace } = vi.hoisted(() => ({ getAnalysisTask: vi.fn(), autoSelectCompetitors: vi.fn(), selectCompetitors: vi.fn(), replace: vi.fn() }));
vi.mock("@/lib/analysis-tasks", () => ({ getAnalysisTask, autoSelectCompetitors, selectCompetitors }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));
import { CandidateConfirmation } from "./candidate-confirmation";

const task = { id: "task-1", space_id: "space-1", title: "写作助手", industry: "AI", product_direction: "写作", keywords: [], known_competitors: [], discovery_mode: "semi_auto", status: "draft", stage: null, completed_at: null, final_competitors: [], candidates: [
  { id: "candidate-1", name: "Example AI", description: "写作产品", source_type: "web", is_selected: false, sort_order: null, evidence: [{ source_title: "Example", source_url: "https://example.com", excerpt: "公开网页摘要" }] },
] };

describe("CandidateConfirmation", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("allows no known competitor and auto-selects evidenced candidates", async () => {
    const interaction = userEvent.setup();
    getAnalysisTask.mockResolvedValueOnce(task); autoSelectCompetitors.mockResolvedValueOnce({ ...task, final_competitors: ["Example AI"] });
    render(<CandidateConfirmation taskId="task-1" />);
    expect(await screen.findByText("https://example.com")).toBeInTheDocument();
    await interaction.click(screen.getByRole("button", { name: "系统自动选择" }));
    await waitFor(() => expect(autoSelectCompetitors).toHaveBeenCalledWith("task-1"));
  });

  it("requires one to three candidates for manual confirmation", async () => {
    const interaction = userEvent.setup(); getAnalysisTask.mockResolvedValueOnce(task);
    render(<CandidateConfirmation taskId="task-1" />);
    await interaction.click(await screen.findByRole("button", { name: "确认并开始分析" }));
    expect(screen.getByRole("alert")).toHaveTextContent("请选择 1 至 3 个竞品");
  });

  it("keeps each candidate checkbox next to its evidence link", async () => {
    getAnalysisTask.mockResolvedValueOnce(task);
    render(<CandidateConfirmation taskId="task-1" />);
    const checkbox = await screen.findByRole("checkbox", { name: "选择 Example AI" });
    const evidenceLink = screen.getByRole("link", { name: "https://example.com" });
    expect(checkbox.closest("label")).toContainElement(evidenceLink);
  });

  it("does not render an unsafe evidence URL as a link", async () => {
    getAnalysisTask.mockResolvedValueOnce({ ...task, candidates: [{ ...task.candidates[0], evidence: [{ source_title: "Unsafe", source_url: "javascript:alert(1)", excerpt: null }] }] });
    render(<CandidateConfirmation taskId="task-1" />);
    expect(await screen.findByText("Unsafe")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Unsafe" })).not.toBeInTheDocument();
  });
});
