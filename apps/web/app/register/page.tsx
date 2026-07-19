import Link from "next/link";
import { AuthForm } from "@/components/auth/auth-form";
import { AuthShell } from "@/components/auth/auth-shell";

export default function RegisterPage() {
  return <AuthShell description="创建账号后开始管理你的竞品分析工作。" footer={<>已有账号？<Link className="font-semibold text-primary underline-offset-4 hover:underline" href="/login">立即登录</Link></>} title="创建账号"><AuthForm mode="register" /></AuthShell>;
}
