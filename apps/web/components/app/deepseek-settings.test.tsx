import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ApiClientError } from "@/lib/api-client";

const { getDeepSeekConfig, saveDeepSeekConfig, replace } = vi.hoisted(() => ({
  getDeepSeekConfig: vi.fn(),
  saveDeepSeekConfig: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("@/lib/model-configs", () => ({ getDeepSeekConfig, saveDeepSeekConfig }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

import { DeepSeekSettings } from "./deepseek-settings";

describe("DeepSeekSettings", () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it("submits the key but never renders it after save", async () => {
    const interaction = userEvent.setup();
    getDeepSeekConfig.mockResolvedValueOnce({
      is_configured: false,
      api_key_hint: null,
      default_model: "deepseek-chat",
    });
    saveDeepSeekConfig.mockResolvedValueOnce({
      is_configured: true,
      api_key_hint: "sk-****1234",
      default_model: "deepseek-chat",
    });
    render(<DeepSeekSettings />);

    await interaction.type(await screen.findByLabelText("DeepSeek API Key"), "sk-secret");
    await interaction.click(screen.getByRole("button", { name: "保存配置" }));

    expect(saveDeepSeekConfig).toHaveBeenCalledWith("sk-secret");
    expect(await screen.findByText("sk-****1234")).toBeInTheDocument();
    expect(screen.queryByDisplayValue("sk-secret")).not.toBeInTheDocument();
    expect(screen.queryByText("sk-secret")).not.toBeInTheDocument();
  });

  it("uses a non-autofilled password field and describes the server-side redaction boundary", async () => {
    getDeepSeekConfig.mockResolvedValueOnce({
      is_configured: true,
      api_key_hint: "sk-****1234",
      default_model: "deepseek-chat",
    });
    render(<DeepSeekSettings />);

    const input = await screen.findByLabelText("DeepSeek API Key");
    expect(input).toHaveAttribute("type", "password");
    expect(input).toHaveAttribute("autocomplete", "off");
    expect(screen.getByText(/服务端返回的脱敏状态/)).toBeInTheDocument();
    expect(screen.queryByText("sk-secret")).not.toBeInTheDocument();
  });

  it("locks the submission while a save request is pending", async () => {
    const interaction = userEvent.setup();
    let resolveSave: (value: { is_configured: boolean; api_key_hint: string; default_model: string }) => void;
    getDeepSeekConfig.mockResolvedValueOnce({
      is_configured: false,
      api_key_hint: null,
      default_model: "deepseek-chat",
    });
    saveDeepSeekConfig.mockImplementationOnce(() => new Promise((resolve) => { resolveSave = resolve; }));
    render(<DeepSeekSettings />);

    await interaction.type(await screen.findByLabelText("DeepSeek API Key"), "sk-secret");
    await interaction.click(screen.getByRole("button", { name: "保存配置" }));

    expect(screen.getByRole("button", { name: "保存中…" })).toBeDisabled();
    expect(screen.getByLabelText("DeepSeek API Key")).toBeDisabled();
    expect(saveDeepSeekConfig).toHaveBeenCalledTimes(1);

    resolveSave!({ is_configured: true, api_key_hint: "sk-****1234", default_model: "deepseek-chat" });
    await screen.findByText("sk-****1234");
  });

  it("redirects an unauthenticated visitor to login", async () => {
    getDeepSeekConfig.mockRejectedValueOnce(new ApiClientError("UNAUTHORIZED", "登录状态无效或已过期"));
    render(<DeepSeekSettings />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});
