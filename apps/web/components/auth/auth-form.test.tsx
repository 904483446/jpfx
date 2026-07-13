import { afterEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const { replace, register, login } = vi.hoisted(() => ({
  replace: vi.fn(),
  register: vi.fn(),
  login: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

vi.mock("@/lib/auth", () => ({ register, login }));

import { AuthForm } from "./auth-form";
import { ApiClientError } from "@/lib/api-client";

const fillRegisterForm = async (user: ReturnType<typeof userEvent.setup>) => {
  await user.type(screen.getByLabelText("昵称"), "测试用户");
  await user.type(screen.getByLabelText("邮箱地址"), "user@example.com");
  await user.type(screen.getByLabelText("密码"), "password-1");
};

describe("AuthForm", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("registers valid input and redirects to login", async () => {
    const user = userEvent.setup();
    register.mockResolvedValueOnce(undefined);
    render(<AuthForm mode="register" />);

    await fillRegisterForm(user);
    await user.click(screen.getByRole("button", { name: "注册" }));

    await waitFor(() => expect(register).toHaveBeenCalledWith({
      displayName: "测试用户", email: "user@example.com", password: "password-1",
    }));
    expect(replace).toHaveBeenCalledWith("/login");
  });

  it("logs in valid input and redirects to the application", async () => {
    const user = userEvent.setup();
    login.mockResolvedValueOnce(undefined);
    render(<AuthForm mode="login" />);

    await user.type(screen.getByLabelText("邮箱地址"), "user@example.com");
    await user.type(screen.getByLabelText("密码"), "password-1");
    await user.click(screen.getByRole("button", { name: "登录" }));

    await waitFor(() => expect(login).toHaveBeenCalledWith({
      email: "user@example.com", password: "password-1",
    }));
    expect(replace).toHaveBeenCalledWith("/app");
  });

  it("shows only the backend Chinese error message", async () => {
    const user = userEvent.setup();
    register.mockRejectedValueOnce(new ApiClientError("EMAIL_EXISTS", "该邮箱已注册", { internal: "do not show" }));
    render(<AuthForm mode="register" />);

    await fillRegisterForm(user);
    await user.click(screen.getByRole("button", { name: "注册" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("该邮箱已注册");
    expect(screen.queryByText("do not show")).not.toBeInTheDocument();
  });

  it("disables the submit button while a request is pending", async () => {
    const user = userEvent.setup();
    let resolveRequest: () => void = () => undefined;
    register.mockImplementationOnce(() => new Promise<void>((resolve) => { resolveRequest = resolve; }));
    render(<AuthForm mode="register" />);

    await fillRegisterForm(user);
    const submit = screen.getByRole("button", { name: "注册" });
    await user.click(submit);

    expect(submit).toBeDisabled();
    await user.click(submit);
    expect(register).toHaveBeenCalledTimes(1);
    resolveRequest();
    await waitFor(() => expect(submit).not.toBeDisabled());
  });

  it("submits only once for synchronous duplicate submit events", async () => {
    const user = userEvent.setup();
    let resolveRequest: () => void = () => undefined;
    register.mockImplementationOnce(() => new Promise<void>((resolve) => { resolveRequest = resolve; }));
    const { container } = render(<AuthForm mode="register" />);

    await fillRegisterForm(user);
    const form = container.querySelector("form");
    expect(form).not.toBeNull();
    act(() => {
      form!.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
      form!.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    });

    expect(register).toHaveBeenCalledTimes(1);
    resolveRequest();
  });

  it.each([
    ["register", "请填写昵称"],
    ["login", "请填写邮箱地址"],
  ] as const)("does not call the API when %s has a required field missing", async (mode, message) => {
    const user = userEvent.setup();
    render(<AuthForm mode={mode} />);

    await user.click(screen.getByRole("button", { name: mode === "register" ? "注册" : "登录" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(message);
    expect(register).not.toHaveBeenCalled();
    expect(login).not.toHaveBeenCalled();
  });

  it.each([
    ["not-an-email", "password-1", "请输入有效的邮箱地址"],
    ["user@example.com", "short", "密码长度应为 8 到 128 个字符"],
  ])("does not call the API for invalid login input", async (email, password, message) => {
    const user = userEvent.setup();
    render(<AuthForm mode="login" />);

    await user.type(screen.getByLabelText("邮箱地址"), email);
    await user.type(screen.getByLabelText("密码"), password);
    await user.click(screen.getByRole("button", { name: "登录" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(message);
    expect(login).not.toHaveBeenCalled();
  });
});
