import type { ReactNode } from "react";
import { BrandMark } from "@/components/brand-mark";

type AuthShellProps = { title: string; description: string; children: ReactNode; footer: ReactNode };

export function AuthShell({ title, description, children, footer }: AuthShellProps) {
  return (
    <main className="auth-dossier min-h-screen bg-background p-4 text-foreground sm:p-8 lg:grid lg:place-items-center">
      <div className="mx-auto grid w-full max-w-5xl overflow-hidden border border-border bg-card shadow-[0_20px_60px_rgb(31_27_23_/_0.12)] lg:grid-cols-[minmax(0,0.9fr)_minmax(28rem,1.1fr)]">
        <aside className="relative border-b border-border bg-secondary p-7 sm:p-10 lg:border-r lg:border-b-0 lg:p-12">
          <div className="absolute inset-x-0 top-0 h-1 bg-primary" />
          <BrandMark />
          <p className="mt-14 font-mono text-xs font-semibold tracking-[0.18em] text-primary">INTELLIGENCE DOSSIER · 01</p>
          <h2 className="mt-4 max-w-sm text-3xl font-semibold tracking-tight text-foreground">证据优先的竞争情报工作台</h2>
          <p className="mt-5 max-w-md text-sm leading-7 text-muted-foreground">从公开信号到可追溯结论，为产品决策保留完整的研究证据链。</p>
          <dl className="mt-10 grid max-w-md gap-4 border-t border-border pt-6 text-sm sm:grid-cols-3 lg:grid-cols-1">
            <div><dt className="font-mono text-[0.7rem] tracking-[0.14em] text-muted-foreground">SOURCE</dt><dd className="mt-1 font-medium">公开情报</dd></div>
            <div><dt className="font-mono text-[0.7rem] tracking-[0.14em] text-muted-foreground">METHOD</dt><dd className="mt-1 font-medium">证据归档</dd></div>
            <div><dt className="font-mono text-[0.7rem] tracking-[0.14em] text-muted-foreground">OUTPUT</dt><dd className="mt-1 font-medium">决策简报</dd></div>
          </dl>
        </aside>
        <section className="bg-card p-7 sm:p-10 lg:p-12">
          <div className="max-w-md">
            <p className="font-mono text-xs font-semibold tracking-[0.18em] text-primary">账户档案</p>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground">{title}</h1>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">{description}</p>
            <div className="mt-9">{children}</div>
            <div className="mt-7 border-t border-border pt-5 text-sm text-muted-foreground">{footer}</div>
          </div>
        </section>
      </div>
    </main>
  );
}
