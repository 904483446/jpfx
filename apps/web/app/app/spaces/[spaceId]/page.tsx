import Link from "next/link";

export default function SpaceDetailPlaceholderPage() {
  return (
    <main className="min-h-screen bg-[#f6f9fb] p-6 text-[#0a1f33] md:p-10">
      <section className="mx-auto max-w-3xl rounded-2xl border border-slate-200 bg-white p-8">
        <p className="text-sm font-medium text-[#14b8a6]">产品空间</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">产品空间详情</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">产品空间详情将在后续任务实现。</p>
        <Link className="mt-6 inline-flex text-sm font-medium text-[#1677ff] hover:underline" href="/app">返回工作台</Link>
      </section>
    </main>
  );
}
