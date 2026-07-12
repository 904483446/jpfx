import Link from "next/link";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  return <AuthShell description="登录后继续管理你的产品空间。" footer={<>还未注册？ <Link className="font-medium text-[#1677ff] hover:underline" href="/register">立即注册</Link></>} title="欢迎回来"><div className="space-y-4"><Input aria-label="邮箱地址" placeholder="邮箱地址" type="email" /><Input aria-label="密码" placeholder="密码" type="password" /><Button className="mt-2 h-10 w-full bg-[#1677ff] hover:bg-[#146be6]" type="button">登录</Button></div></AuthShell>;
}
