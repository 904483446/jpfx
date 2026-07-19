import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ApiClientError } from "@/lib/api-client";

const { getCurrentUser, searchSpaceDocuments, replace } = vi.hoisted(() => ({
  getCurrentUser: vi.fn(),
  searchSpaceDocuments: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("@/lib/auth", () => ({ getCurrentUser }));
vi.mock("@/lib/retrieval", () => ({ searchSpaceDocuments }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import { SpaceRetrieval } from "./space-retrieval";

describe("SpaceRetrieval", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("renders returned source snippets with a similarity score, not a confidence claim", async () => {
    const interaction = userEvent.setup();
    getCurrentUser.mockResolvedValueOnce({ id: "user-1" });
    searchSpaceDocuments.mockResolvedValueOnce({
      results: [{ content: "目标用户是小型团队", filename: "brief.md", chunk_index: 2, similarity: 0.92 }],
    });
    render(<SpaceRetrieval spaceId="space-1" />);

    await interaction.type(await screen.findByLabelText("检索问题"), "目标用户是谁");
    await interaction.click(screen.getByRole("button", { name: "检索" }));

    expect(await screen.findByText("目标用户是小型团队")).toBeInTheDocument();
    expect(screen.getByText(/brief.md.*片段 3.*0.92/)).toBeInTheDocument();
    expect(screen.getAllByText(/相似度 0.92/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/可信度/)).not.toBeInTheDocument();
  });

  it("shows a Chinese empty-result hint", async () => {
    const interaction = userEvent.setup();
    getCurrentUser.mockResolvedValueOnce({ id: "user-1" });
    searchSpaceDocuments.mockResolvedValueOnce({ results: [] });
    render(<SpaceRetrieval spaceId="space-1" />);

    await interaction.type(await screen.findByLabelText("检索问题"), "不存在的问题");
    await interaction.click(screen.getByRole("button", { name: "检索" }));

    expect(await screen.findByText("没有找到相关文档片段")).toBeInTheDocument();
  });

  it("redirects an unauthenticated visitor", async () => {
    getCurrentUser.mockRejectedValueOnce(new ApiClientError("UNAUTHORIZED", "登录状态无效或已过期"));
    render(<SpaceRetrieval spaceId="space-1" />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});
