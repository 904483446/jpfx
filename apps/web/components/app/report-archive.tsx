import type { CompetitorReport, EvidenceSourceType, ReportCompetitor, ReportEvidence } from "@/lib/reports";

const sourceLabels: Record<EvidenceSourceType, string> = {
  web: "公开网页",
  private_knowledge: "私有知识库",
  model_inference: "模型推断",
};

const sourceStyles: Record<EvidenceSourceType, string> = {
  web: "border-primary/20 bg-primary/10 text-primary",
  private_knowledge: "border-border bg-secondary text-secondary-foreground",
  model_inference: "border-destructive/20 bg-destructive/10 text-destructive",
};

/** Pure report presentation: data loading, routing and downloads stay in ReportDetail. */
export function ReportArchive({ report, evidence }: { report: CompetitorReport; evidence: ReportEvidence[] }) {
  const competitors = report.structured_json.competitors ?? [];
  const recommendations = competitors.flatMap((item) => item.recommendations ?? []);
  const risks = competitors.flatMap((item) => item.risks ?? []);

  return <div className="mt-8 grid gap-6">
    <section className="overflow-hidden rounded-2xl border border-primary/20 bg-muted/70 shadow-sm">
      <div className="border-b border-border px-5 py-3"><p className="text-xs font-semibold tracking-[0.2em] text-primary">REPORT ARCHIVE · {String(report.version).padStart(2, "0")}</p></div>
      <div className="p-5"><h2 className="text-lg font-semibold text-foreground">执行摘要</h2><p className="mt-3 leading-7 text-muted-foreground">{report.structured_json.executive_summary ?? "暂无执行摘要。"}</p></div>
    </section>
    <section><h2 className="mb-3 text-lg font-semibold text-foreground">竞品对比</h2><div className="grid gap-4 lg:grid-cols-2">{competitors.map((competitor) => <CompetitorCard competitor={competitor} key={competitor.name} />)}</div></section>
    <ListSection title="产品建议" items={recommendations} tone="text-primary" />
    <ListSection title="风险与不确定性" items={risks} tone="text-destructive" />
    <EvidenceLedger evidence={evidence} />
  </div>;
}

function CompetitorCard({ competitor }: { competitor: ReportCompetitor }) { return <article className="rounded-2xl border border-border bg-card p-5 shadow-sm"><h3 className="text-xl font-semibold text-foreground">{competitor.name}</h3>{competitor.positioning ? <p className="mt-2 text-sm text-muted-foreground">{competitor.positioning}</p> : null}<Fact label="核心功能" values={competitor.core_features} /><Fact label="优势" values={competitor.strengths} /><Fact label="不足" values={competitor.weaknesses} /><Fact label="差异化机会" values={competitor.differentiation_opportunities} /></article>; }
function Fact({ label, values }: { label: string; values?: string[] }) { return values?.length ? <div className="mt-4"><p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{label}</p><p className="mt-1 text-sm leading-6 text-foreground/80">{values.join(" · ")}</p></div> : null; }
function ListSection({ title, items, tone }: { title: string; items: string[]; tone: string }) { return <section className="rounded-2xl border border-border bg-card p-5 shadow-sm"><h2 className="text-lg font-semibold text-foreground">{title}</h2>{items.length ? <ul className={`mt-3 space-y-2 text-sm ${tone}`}>{items.map((item, index) => <li key={`${item}-${index}`}>• {item}</li>)}</ul> : <p className="mt-3 text-sm text-muted-foreground">暂无内容。</p>}</section>; }

function EvidenceLedger({ evidence }: { evidence: ReportEvidence[] }) { return <section className="rounded-2xl border border-border bg-card shadow-sm"><div className="border-b border-border px-5 py-4"><p className="text-xs font-semibold tracking-[0.2em] text-muted-foreground">PROVENANCE LEDGER</p><h2 className="mt-1 text-lg font-semibold text-foreground">证据账本</h2><p className="mt-1 text-sm text-muted-foreground">结论与来源分开呈现；模型正文不能替代可追溯的证据。</p></div><div className="divide-y divide-border">{evidence.map((item) => <article className="p-5" key={item.id}><div className="flex flex-wrap items-center gap-2"><span className={`rounded-full border px-2.5 py-1 text-xs font-medium ${sourceStyles[item.source_type]}`}>{sourceLabels[item.source_type]}</span>{isSafeExternalUrl(item.source_url) ? <a className="text-sm font-medium text-primary underline underline-offset-4" href={item.source_url} rel="noreferrer" target="_blank">{item.source_title}</a> : <p className="text-sm font-medium text-foreground">{item.source_title}</p>}</div>{item.quote ? <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.quote}</p> : null}{item.source_type === "model_inference" ? <p className="mt-2 text-xs text-destructive">模型推断不构成事实证据，需进一步验证。</p> : null}</article>)}{evidence.length === 0 ? <p className="p-5 text-sm text-muted-foreground">暂无可展示的证据来源。</p> : null}</div></section>; }

export function isSafeExternalUrl(value: string | null): value is string {
  if (!value) return false;
  try {
    const url = new URL(value);
    return (url.protocol === "http:" || url.protocol === "https:") && Boolean(url.hostname);
  } catch { return false; }
}
