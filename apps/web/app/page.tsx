import Link from "next/link";

import { BrandMark } from "@/components/brand-mark";
import { Steps } from "@/components/landing/steps";

const workflow = ["资料入库", "分析任务", "报告交付"];

function ProductWorkflowPreview() {
  return (
    <section aria-label="产品流程预览" className="border border-border bg-card p-5 shadow-sm sm:p-7">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <p className="font-mono text-xs tracking-[0.16em] text-muted-foreground">PRODUCT WORKFLOW</p>
        <span className="text-xs font-medium text-primary">研究流程</span>
      </div>
      <ol className="mt-7 space-y-3">
        {workflow.map((item, index) => (
          <li className="grid grid-cols-[2rem_1fr] items-center border border-border bg-background p-4" key={item}>
            <span className="font-mono text-sm text-primary">0{index + 1}</span>
            <span className="font-medium text-foreground">{item}</span>
          </li>
        ))}
      </ol>
      <p className="mt-5 border-t border-border pt-4 text-sm leading-6 text-muted-foreground">
        每一步都保留可核查的来源与研究记录。
      </p>
    </section>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="mx-auto flex min-h-20 max-w-7xl items-center justify-between gap-6 border-b border-border px-6 py-5 lg:px-8">
        <BrandMark />
        <nav aria-label="主导航" className="flex items-center gap-5 text-sm text-muted-foreground">
          <a className="hidden hover:text-foreground sm:inline" href="#product">
            产品介绍
          </a>
          <Link className="hover:text-foreground" href="/login">
            登录
          </Link>
          <Link className="border border-border px-3 py-2 font-medium text-foreground hover:bg-muted" href="/register">
            创建账户
          </Link>
        </nav>
      </header>

      <section className="mx-auto grid max-w-7xl gap-10 px-6 py-14 lg:grid-cols-[minmax(0,1.1fr)_minmax(22rem,0.9fr)] lg:gap-16 lg:px-8 lg:py-24" id="product">
        <div className="flex flex-col justify-between">
          <div>
            <p className="font-mono text-xs tracking-[0.18em] text-primary">证据驱动的竞品情报</p>
            <h1 className="mt-6 max-w-3xl text-4xl font-semibold leading-[1.12] tracking-tight sm:text-5xl lg:text-6xl">
              把竞品洞察变成可验证的决策。
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
              为产品团队整理资料、组织分析，并将结论与证据清晰地带回每一次决策讨论。
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link className="inline-flex min-h-11 items-center justify-center bg-primary px-5 text-sm font-medium text-primary-foreground hover:bg-primary/85" href="/login">
                登录
              </Link>
              <Link className="inline-flex min-h-11 items-center justify-center border border-border bg-card px-5 text-sm font-medium text-card-foreground hover:bg-muted" href="/register">
                创建账户
              </Link>
            </div>
          </div>
          <p className="mt-12 max-w-xl border-l-2 border-primary pl-4 text-sm leading-6 text-muted-foreground lg:mt-20">
            不是替你做判断，而是让判断所依据的材料、分析过程和待确认事项更容易被看见。
          </p>
        </div>

        <ProductWorkflowPreview />
      </section>

      <section className="mx-auto max-w-7xl border-t border-border px-6 pb-16 lg:px-8 lg:pb-24">
        <Steps />
      </section>
    </main>
  );
}
