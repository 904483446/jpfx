import Link from "next/link";

import { BrandMark } from "@/components/brand-mark";
import { Steps } from "@/components/landing/steps";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f6f9fb] text-[#0a1f33]">
      <header className="mx-auto flex h-20 max-w-6xl items-center justify-between px-6">
        <BrandMark />
        <nav aria-label="主导航" className="flex items-center gap-5 text-sm text-slate-600">
          <a href="#product">产品介绍</a>
          <Link href="/login">登录</Link>
          <Link href="/register">注册</Link>
        </nav>
      </header>
      <section className="mx-auto max-w-6xl px-6 pb-20 pt-20 md:pt-28" id="product">
        <p className="text-sm font-semibold tracking-[0.18em] text-[#14b8a6]">AI COMPETITOR INTELLIGENCE</p>
        <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight tracking-tight md:text-6xl">把竞品洞察变成可验证的决策。</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">汇集私有资料与公开信息，生成有来源、有证据、有不确定性提示的竞品分析报告。</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button className="h-11 bg-[#1677ff] px-5 hover:bg-[#146be6]" render={<Link href="/login" />}>登录</Button>
          <Button className="h-11 border-slate-200 bg-white px-5 text-[#0a1f33] hover:bg-slate-50" render={<Link href="/register" />} variant="outline">注册</Button>
        </div>
        <Steps />
      </section>
    </main>
  );
}
