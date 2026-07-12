import type { ReactNode } from "react";
import { BrandMark } from "@/components/brand-mark";

const navigationItems = ["概览", "产品空间", "知识库", "设置"];

export function AppShell({ children }: { children: ReactNode }) {
  return <main className="min-h-screen bg-[#f6f9fb] text-[#0a1f33]"><header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6"><BrandMark /><span className="text-sm text-slate-500">未登录状态占位</span></header><div className="flex min-h-[calc(100vh-4rem)]"><aside className="w-52 bg-[#0a1f33] px-4 py-6 text-slate-200"><nav aria-label="应用导航" className="space-y-1">{navigationItems.map((item, index) => <span className={index === 0 ? "block rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-white" : "block rounded-lg px-3 py-2 text-sm"} key={item}>{item}</span>)}</nav></aside><section className="flex-1 p-6 md:p-10">{children}</section></div></main>;
}
