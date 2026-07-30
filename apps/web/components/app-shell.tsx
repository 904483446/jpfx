import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrandMark } from "@/components/brand-mark";
import { LogoutControl } from "@/components/auth/logout-control";

const navigationItems = [
  { href: "/app", label: "工作台", note: "空间总览" },
  { href: "/app/spaces", label: "产品空间", note: "资料与洞察" },
  { href: "/app/tasks", label: "分析任务", note: "研究队列" },
  { href: "/app/reports", label: "报告中心", note: "交付归档" },
  { href: "/app/settings", label: "设置", note: "账号与模型" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="app-dossier min-h-screen bg-background text-foreground" data-testid="app-dossier">
      <div className="grid min-h-screen lg:grid-cols-[15rem_minmax(0,1fr)]">
        <aside aria-label="主导航" className="border-b border-border bg-card lg:border-r lg:border-b-0">
          <div className="flex h-full flex-col px-5 py-6 lg:sticky lg:top-0 lg:min-h-screen">
            <BrandMark />
            <nav aria-label="主导航" className="mt-10">
              <p className="font-mono text-[0.68rem] tracking-[0.16em] text-muted-foreground">目录</p>
              <ul className="mt-3 space-y-1">
                {navigationItems.map((item) => {
                  const isCurrent = pathname === item.href || (item.href !== "/app" && pathname.startsWith(`${item.href}/`));

                  return <li key={item.href}><Link aria-current={isCurrent ? "page" : undefined} className={`group block border px-3 py-2.5 transition-colors focus-visible:border-ring ${isCurrent ? "border-primary/35 bg-primary/10 text-primary" : "border-transparent hover:border-border hover:bg-muted"}`} href={item.href}><span className="block text-sm font-medium">{item.label}</span><span className={`mt-0.5 block text-xs ${isCurrent ? "text-primary/80" : "text-muted-foreground group-hover:text-foreground"}`}>{item.note}</span></Link></li>;
                })}
              </ul>
            </nav>
            <p className="mt-auto hidden border-t border-border pt-4 text-xs leading-5 text-muted-foreground lg:block">以可追溯证据组织每一次竞品研究。</p>
          </div>
        </aside>
        <div className="min-w-0"><header className="context-bar flex min-h-16 items-center justify-between gap-4 border-b border-border bg-background px-5 py-3 sm:px-8" data-testid="context-bar"><div><p className="font-mono text-[0.68rem] tracking-[0.16em] text-muted-foreground">竞品智研台</p><p className="text-sm font-medium">工作台 / 产品空间</p></div><div className="flex items-center gap-4"><Link className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline" href="/app/settings">账户设置</Link><LogoutControl /></div></header><main aria-label="主内容" className="px-5 py-8 sm:px-8 lg:px-12 lg:py-10">{children}</main></div>
      </div>
    </div>
  );
}
