import Link from "next/link";
import { AppShell } from "@/components/app-shell";

export default function TasksPage() {
  return (
    <AppShell>
      <section className="mx-auto max-w-4xl">
        <p className="font-mono text-[0.68rem] tracking-[0.16em] text-primary">分析任务</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-foreground">研究队列</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
          分析任务会绑定到一个产品空间，以便保留资料来源、候选证据和最终结论的上下文。
        </p>
        <div className="mt-8 rounded-lg border border-dashed border-border bg-muted/30 p-6">
          <p className="font-medium text-foreground">尚无可展示队列</p>
          <h2 className="mt-5 text-lg font-semibold text-foreground">从产品空间发起分析</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            进入一个产品空间后，即可基于已归集资料创建分析任务。
          </p>
          <Link className="mt-4 inline-flex text-sm font-medium text-primary hover:underline" href="/app/spaces">
            进入产品空间
          </Link>
        </div>
      </section>
    </AppShell>
  );
}
