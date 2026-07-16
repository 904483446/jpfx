import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ApiClientError } from "@/lib/api-client";

const { getCurrentUser, listDocuments, uploadDocument, deleteDocument, indexDocument, replace } = vi.hoisted(() => ({
  getCurrentUser: vi.fn(),
  listDocuments: vi.fn(),
  uploadDocument: vi.fn(),
  deleteDocument: vi.fn(),
  indexDocument: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("@/lib/auth", () => ({ getCurrentUser }));
vi.mock("@/lib/documents", () => ({ listDocuments, uploadDocument, deleteDocument }));
vi.mock("@/lib/retrieval", () => ({ indexDocument }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import { SpaceDocuments } from "./space-documents";

const user = { id: "user-1", display_name: "测试用户", email: "user@example.com" };
const document = {
  id: "document-1", filename: "brief.pdf", file_type: "pdf", file_size: 2048,
  status: "uploaded", error_message: null,
  created_at: "2026-07-15T00:00:00Z", updated_at: "2026-07-15T00:00:00Z",
};

describe("SpaceDocuments", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("loads and renders current space documents", async () => {
    getCurrentUser.mockResolvedValueOnce(user);
    listDocuments.mockResolvedValueOnce([document]);
    render(<SpaceDocuments spaceId="space-1" />);
    expect(await screen.findByRole("heading", { name: "文档管理" })).toBeInTheDocument();
    expect(screen.getByText("brief.pdf")).toBeInTheDocument();
    expect(screen.getByText(/PDF.*2048 B.*2026/)).toBeInTheDocument();
  });

  it("redirects an unauthenticated visitor", async () => {
    getCurrentUser.mockRejectedValueOnce(new ApiClientError("UNAUTHORIZED", "登录状态无效或已过期"));
    render(<SpaceDocuments spaceId="space-1" />);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });

  it("uploads a selected file then refreshes the list", async () => {
    const interaction = userEvent.setup();
    getCurrentUser.mockResolvedValueOnce(user);
    listDocuments.mockResolvedValueOnce([]).mockResolvedValueOnce([document]);
    uploadDocument.mockResolvedValueOnce(document);
    render(<SpaceDocuments spaceId="space-1" />);
    const file = new File(["content"], "brief.txt", { type: "text/plain" });
    await interaction.upload(await screen.findByLabelText("选择文档"), file);
    await interaction.click(screen.getByRole("button", { name: "上传文档" }));
    await waitFor(() => expect(uploadDocument).toHaveBeenCalledWith("space-1", file));
    expect(await screen.findByText("brief.pdf")).toBeInTheDocument();
  });

  it("deletes a document then refreshes the list", async () => {
    const interaction = userEvent.setup();
    getCurrentUser.mockResolvedValueOnce(user);
    listDocuments.mockResolvedValueOnce([document]).mockResolvedValueOnce([]);
    render(<SpaceDocuments spaceId="space-1" />);
    await interaction.click(await screen.findByRole("button", { name: "删除 brief.pdf" }));
    await waitFor(() => expect(deleteDocument).toHaveBeenCalledWith("document-1"));
    expect(await screen.findByText("还没有上传文档")).toBeInTheDocument();
  });

  it("indexes an uploaded document then refreshes the list", async () => {
    const interaction = userEvent.setup();
    getCurrentUser.mockResolvedValueOnce(user);
    listDocuments.mockResolvedValueOnce([document]).mockResolvedValueOnce([{ ...document, status: "indexed" }]);
    indexDocument.mockResolvedValueOnce({ ...document, status: "indexed" });
    render(<SpaceDocuments spaceId="space-1" />);

    await interaction.click(await screen.findByRole("button", { name: "开始索引 brief.pdf" }));

    await waitFor(() => expect(indexDocument).toHaveBeenCalledWith("document-1"));
    expect(await screen.findByText(/已索引/)).toBeInTheDocument();
  });

  it("disables indexing while a document is processing", async () => {
    getCurrentUser.mockResolvedValueOnce(user);
    listDocuments.mockResolvedValueOnce([{ ...document, status: "processing" }]);
    render(<SpaceDocuments spaceId="space-1" />);

    expect(await screen.findByRole("button", { name: "正在处理 brief.pdf" })).toBeDisabled();
  });
});
