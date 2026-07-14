import Link from "next/link";
import { AuthForm } from "@/components/auth/auth-form";
import { AuthShell } from "@/components/auth/auth-shell";

export default function LoginPage() {
  return <AuthShell description="登录后继续管理你的产品空间。" footer={<>还未注册？<Link className="font-medium text-[#1677ff] hover:underline" href="/register">立即注册</Link></>} title="欢迎回来"><AuthForm mode="login" /></AuthShell>;
}
