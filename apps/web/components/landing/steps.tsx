const steps = [
  { number: "01", title: "资料入库", description: "将已有材料沉淀到产品空间，保留可追溯的来源。" },
  { number: "02", title: "分析任务", description: "围绕明确的问题组织分析，而非堆叠结论。" },
  { number: "03", title: "报告交付", description: "让洞察、证据与待确认项一同进入决策讨论。" },
];

export function Steps() {
  return (
    <ol className="mt-14 grid gap-4 md:grid-cols-[1.1fr_0.8fr_1.3fr] md:items-start">
      {steps.map((step, index) => (
        <li
          className={`border border-border bg-card p-5 ${index === 1 ? "md:mt-8" : ""} ${index === 2 ? "md:mt-3 md:p-7" : ""}`}
          key={step.number}
        >
          <span className="font-mono text-sm text-primary">{step.number}</span>
          <h2 className="mt-5 text-lg font-semibold text-card-foreground">{step.title}</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">{step.description}</p>
        </li>
      ))}
    </ol>
  );
}
