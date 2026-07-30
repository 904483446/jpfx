import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ApiClientError } from "@/lib/api-client";

const { listSpaces, replace } = vi.hoisted(() => ({ listSpaces: vi.fn(), replace: vi.fn() }));
vi.mock("@/lib/spaces", () => ({ listSpaces }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import { DashboardSpaces } from "./dashboard-spaces";

const currentUser = { id: "user-1", display_name: "测试用户", email: "user@example.com", is_admin: false, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" };
const space = { id: "space-1", name: "企业知识库 Copilot", industry: "企业服务", product_direction: "AI 知识库", description: null, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" };

describe("DashboardSpaces", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("shows a loading skeleton before the product spaces arrive", async () => {
    listSpaces.mockImplementationOnce(() => new Promise(() => undefined));
    render(<DashboardSpaces user={currentUser} />);

    expect(screen.getByTestId("space-list-skeleton")).toBeInTheDocument();
    await waitFor(() => expect(listSpaces).toHaveBeenCalledTimes(1));
  });

  it("gives an empty workspace a primary action to create its first product space", async () => {
    const user = userEvent.setup();
    listSpaces.mockResolvedValueOnce([]);
    render(<DashboardSpaces user={currentUser} />);

    await screen.findByText("还没有产品空间");
    await user.click(screen.getByRole("button", { name: "创建第一个产品空间" }));
    expect(screen.getByRole("dialog", { name: "新建产品空间" })).toBeInTheDocument();
  });

  it("renders current user and returned space cards", async () => {
    listSpaces.mockResolvedValueOnce([space]);
    render(<DashboardSpaces user={currentUser} />);
    expect(screen.getByText("正在加载产品空间…")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "研究总览" })).toBeInTheDocument();
    expect(screen.getByText(/测试用户/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "企业知识库 Copilot" })).toHaveAttribute("href", "/app/spaces/space-1");
  });

  it("uses a research overview heading while keeping the signed-in user visible", async () => {
    listSpaces.mockResolvedValueOnce([space]);
    render(<DashboardSpaces user={currentUser} />);

    expect(await screen.findByRole("heading", { name: "研究总览" })).toBeInTheDocument();
    expect(screen.getByText(/测试用户/)).toBeInTheDocument();
  });

  it("renders empty state and opens create dialog", async () => {
    const user = userEvent.setup();
    listSpaces.mockResolvedValueOnce([]);
    render(<DashboardSpaces user={currentUser} />);
    expect(await screen.findByText("还没有产品空间")).toBeInTheDocument();
    await user.click(screen.getAllByRole("button", { name: "新建产品空间" })[0]);
    expect(screen.getByRole("dialog", { name: "新建产品空间" })).toBeInTheDocument();
  });

  it("redirects only an unauthorized list request", async () => {
    listSpaces.mockRejectedValueOnce(new ApiClientError("UNAUTHORIZED", "登录状态无效或已过期"));
    render(<DashboardSpaces user={currentUser} />);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});
