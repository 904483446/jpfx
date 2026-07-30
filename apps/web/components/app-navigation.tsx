"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigationItems = [
  { href: "/app", label: "工作台", note: "空间总览" },
  { href: "/app/spaces", label: "产品空间", note: "资料与洞察" },
  { href: "/app/tasks", label: "分析任务", note: "研究队列" },
  { href: "/app/reports", label: "报告中心", note: "交付归档" },
  { href: "/app/settings", label: "设置", note: "账号与模型" },
];

export function AppNavigation() {
  const pathname = usePathname();

  return (
    <nav aria-label="主导航" className="mt-10">
      <p className="font-mono text-[0.68rem] tracking-[0.16em] text-muted-foreground">目录</p>
      <ul className="mt-3 space-y-1">
        {navigationItems.map((item) => {
          const isCurrent = pathname === item.href || (item.href !== "/app" && pathname.startsWith(`${item.href}/`));

          return <li key={item.href}><Link aria-current={isCurrent ? "page" : undefined} className={`group block border px-3 py-2.5 transition-colors focus-visible:border-ring ${isCurrent ? "border-primary/35 bg-primary/10 text-primary" : "border-transparent hover:border-border hover:bg-muted"}`} href={item.href}><span className="block text-sm font-medium">{item.label}</span><span className={`mt-0.5 block text-xs ${isCurrent ? "text-primary/80" : "text-muted-foreground group-hover:text-foreground"}`}>{item.note}</span></Link></li>;
        })}
      </ul>
    </nav>
  );
}
