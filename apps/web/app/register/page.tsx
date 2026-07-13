import Link from "next/link";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function RegisterPage() {
  return <AuthShell description="创建账号后开始管理你的竞品分析工作。" footer={<>已有账号？ <Link className="font-medium text-[#1677ff] hover:underline" href="/login">立即登录</Link></>} title="创建账号"><div className="space-y-4"><Input aria-label="昵称" placeholder="昵称" type="text" /><Input aria-label="邮箱地址" placeholder="邮箱地址" type="email" /><Input aria-label="密码" placeholder="密码" type="password" /><Button className="mt-2 h-10 w-full bg-[#1677ff] hover:bg-[#146be6]" type="button">注册</Button></div></AuthShell>;
}
