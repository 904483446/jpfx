import type { ReactNode } from "react";
import { BrandMark } from "@/components/brand-mark";

const navigationItems = ["概览", "产品空间", "知识库", "设置"];

export function AppShell({ children }: { children: ReactNode }) {
  return <main className="min-h-screen bg-[#f6f9fb] text-[#0a1f33]"><header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6"><BrandMark /><span className="text-sm text-slate-500">未登录状态占位</span></header><div className="flex min-h-[calc(100vh-4rem)]"><aside className="w-52 bg-[#0a1f33] px-4 py-6 text-slate-200"><section aria-label="应用功能占位"><p className="px-3 pb-3 text-xs font-medium text-slate-400">应用功能占位</p><ul className="space-y-1">{navigationItems.map((item, index) => <li className={index === 0 ? "rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-white" : "rounded-lg px-3 py-2 text-sm"} key={item}>{item}</li>)}</ul></section></aside><section className="flex-1 p-6 md:p-10">{children}</section></div></main>;
}
