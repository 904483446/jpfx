const steps = [{ number: "01", title: "整理资料", description: "沉淀公开信息与已有材料。" }, { number: "02", title: "分析竞品", description: "把观察转化为结构化洞察。" }, { number: "03", title: "输出报告", description: "形成可验证的决策依据。" }];

export function Steps() {
  return <ol className="mt-16 grid gap-4 sm:grid-cols-3">{steps.map((step) => <li className="rounded-xl border border-slate-200 bg-white p-5" key={step.number}><span className="text-xl font-semibold text-[#1677ff]">{step.number}</span><h2 className="mt-2 font-semibold text-[#0a1f33]">{step.title}</h2><p className="mt-1 text-sm leading-6 text-slate-500">{step.description}</p></li>)}</ol>;
}
