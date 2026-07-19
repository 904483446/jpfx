import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ApiClientError } from "@/lib/api-client";

const { createSpace } = vi.hoisted(() => ({ createSpace: vi.fn() }));
vi.mock("@/lib/spaces", () => ({ createSpace }));

import { SpaceCreateDialog } from "./space-create-dialog";

const space = { id: "space-1", name: "企业知识库 Copilot", industry: null, product_direction: null, description: null, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" };

describe("SpaceCreateDialog", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("keeps the original field ids in the dossier dialog", () => {
    render(<SpaceCreateDialog open onOpenChange={vi.fn()} onCreated={vi.fn()} />);

    expect(screen.getByLabelText("空间名称")).toHaveAttribute("id", "space-name");
    expect(screen.getByLabelText("行业")).toHaveAttribute("id", "space-industry");
    expect(screen.getByLabelText("产品方向")).toHaveAttribute("id", "space-product-direction");
    expect(screen.getByLabelText("描述")).toHaveAttribute("id", "space-description");
  });

  it("does not request creation when the name is blank", async () => {
    const user = userEvent.setup();
    render(<SpaceCreateDialog open onOpenChange={vi.fn()} onCreated={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "创建产品空间" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("请填写产品空间名称");
    expect(createSpace).not.toHaveBeenCalled();
  });

  it("submits fields once and reports the created space", async () => {
    const user = userEvent.setup();
    createSpace.mockResolvedValueOnce(space);
    const onCreated = vi.fn();
    const onOpenChange = vi.fn();
    render(<SpaceCreateDialog open onOpenChange={onOpenChange} onCreated={onCreated} />);
    await user.type(screen.getByLabelText("空间名称"), "企业知识库 Copilot");
    await user.type(screen.getByLabelText("行业"), "企业服务");
    await user.type(screen.getByLabelText("产品方向"), "AI 知识库");
    await user.click(screen.getByRole("button", { name: "创建产品空间" }));
    await waitFor(() => expect(createSpace).toHaveBeenCalledTimes(1));
    expect(onOpenChange).toHaveBeenCalledWith(false);
    expect(onCreated).toHaveBeenCalledWith(space);
  });

  it("keeps input when the backend returns a Chinese error", async () => {
    const user = userEvent.setup();
    createSpace.mockRejectedValueOnce(new ApiClientError("VALIDATION_ERROR", "产品空间名称不能为空"));
    render(<SpaceCreateDialog open onOpenChange={vi.fn()} onCreated={vi.fn()} />);
    await user.type(screen.getByLabelText("空间名称"), "测试空间");
    await user.click(screen.getByRole("button", { name: "创建产品空间" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("产品空间名称不能为空");
    expect(screen.getByLabelText("空间名称")).toHaveValue("测试空间");
  });
});
