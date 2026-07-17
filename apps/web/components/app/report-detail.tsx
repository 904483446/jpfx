"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ApiClientError } from "@/lib/api-client";
import { downloadReport, getReport, getReportEvidence, type CompetitorReport, type EvidenceSourceType, type ReportCompetitor, type ReportEvidence } from "@/lib/reports";

const sourceLabels: Record<EvidenceSourceType, string> = { web: "公开网页", private_knowledge: "私有知识库", model_inference: "模型推断" };
const sourceStyles: Record<EvidenceSourceType, string> = { web: "bg-cyan-400/15 text-cyan-200", private_knowledge: "bg-violet-400/15 text-violet-200", model_inference: "bg-amber-400/15 text-amber-200" };

export function ReportDetail({ reportId }: { reportId: string }) {
  const { replace } = useRouter();
  const [report, setReport] = useState<CompetitorReport | null>(null);
  const [evidence, setEvidence] = useState<ReportEvidence[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<"pdf" | "docx" | null>(null);
  const load = useCallback(async () => {
    try {
      const [nextReport, nextEvidence] = await Promise.all([getReport(reportId), getReportEvidence(reportId)]);
      if (nextReport) setReport(nextReport);
      if (nextEvidence) setEvidence(nextEvidence);
    } catch (caught) {
      if (caught instanceof ApiClientError && caught.code === "UNAUTHORIZED") { replace("/login"); return; }
      setError(caught instanceof ApiClientError ? caught.message : "加载报告失败，请稍后重试。");
    }
  }, [replace, reportId]);
  useEffect(() => { void Promise.resolve().then(load); }, [load]);
  const exportFile = async (format: "pdf" | "docx") => {
    if (downloading) return;
    setDownloading(format); setError(null);
    try { await downloadReport(reportId, format); }
    catch (caught) {
      if (caught instanceof ApiClientError && caught.code === "UNAUTHORIZED") replace("/login");
      else setError(caught instanceof ApiClientError ? caught.message : "下载报告失败，请稍后重试。");
    } finally { setDownloading(null); }
  };

  return <section className="mx-auto max-w-6xl text-slate-100">
    <div className="rounded-3xl border border-slate-700 bg-slate-950 p-6 shadow-2xl shadow-slate-950/30 md:p-8">
      <div className="flex flex-col justify-between gap-5 md:flex-row md:items-start"><div><p className="text-sm font-medium text-cyan-300">证据驱动报告</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">{report?.title ?? "正在加载报告…"}</h1>{report ? <p className="mt-3 text-sm text-slate-400">生成于 {new Date(report.created_at).toLocaleString("zh-CN")}</p> : null}</div><div className="flex gap-3"><Button disabled={!report || downloading !== null} onClick={() => void exportFile("pdf")} type="button">{downloading === "pdf" ? "正在下载…" : "下载 PDF"}</Button><Button disabled={!report || downloading !== null} onClick={() => void exportFile("docx")} type="button" variant="outline">{downloading === "docx" ? "正在下载…" : "下载 DOCX"}</Button></div></div>
      {error ? <p className="mt-5 text-sm text-red-300" role="alert">{error}</p> : null}
      {report ? <ReportBody report={report} evidence={evidence} /> : null}
    </div>
  </section>;
}

function ReportBody({ report, evidence }: { report: CompetitorReport; evidence: ReportEvidence[] }) {
  const competitors = report.structured_json.competitors ?? [];
  const recommendations = competitors.flatMap((item) => item.recommendations ?? []);
  const risks = competitors.flatMap((item) => item.risks ?? []);
  return <div className="mt-8 grid gap-6"><section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5"><h2 className="text-lg font-semibold">执行摘要</h2><p className="mt-3 leading-7 text-slate-300">{report.structured_json.executive_summary ?? "暂无执行摘要。"}</p></section><section><h2 className="mb-3 text-lg font-semibold">竞品对比</h2><div className="grid gap-4 lg:grid-cols-2">{competitors.map((competitor) => <CompetitorCard competitor={competitor} key={competitor.name} />)}</div></section><ListSection title="产品建议" items={recommendations} tone="text-emerald-200" /><ListSection title="风险与不确定性" items={risks} tone="text-amber-200" /><EvidenceLedger evidence={evidence} /></div>;
}

function CompetitorCard({ competitor }: { competitor: ReportCompetitor }) { return <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><h3 className="text-xl font-semibold text-cyan-100">{competitor.name}</h3>{competitor.positioning ? <p className="mt-2 text-sm text-slate-400">{competitor.positioning}</p> : null}<Fact label="核心功能" values={competitor.core_features} /><Fact label="优势" values={competitor.strengths} /><Fact label="不足" values={competitor.weaknesses} /><Fact label="差异化机会" values={competitor.differentiation_opportunities} /></article>; }
function Fact({ label, values }: { label: string; values?: string[] }) { return values?.length ? <div className="mt-4"><p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p><p className="mt-1 text-sm leading-6 text-slate-300">{values.join(" · ")}</p></div> : null; }
function ListSection({ title, items, tone }: { title: string; items: string[]; tone: string }) { return <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5"><h2 className="text-lg font-semibold">{title}</h2>{items.length ? <ul className={`mt-3 space-y-2 text-sm ${tone}`}>{items.map((item, index) => <li key={`${item}-${index}`}>• {item}</li>)}</ul> : <p className="mt-3 text-sm text-slate-500">暂无内容。</p>}</section>; }
function EvidenceLedger({ evidence }: { evidence: ReportEvidence[] }) { return <section className="rounded-2xl border border-slate-700 bg-slate-950 p-5"><div><h2 className="text-lg font-semibold">证据来源</h2><p className="mt-1 text-sm text-slate-400">结论与来源分开呈现；模型正文不能替代可追溯的证据。</p></div><div className="mt-4 space-y-3">{evidence.map((item) => <article className="rounded-xl border border-slate-800 bg-slate-900 p-4" key={item.id}><div className="flex flex-wrap items-center gap-2"><span className={`rounded-full px-2.5 py-1 text-xs font-medium ${sourceStyles[item.source_type]}`}>{sourceLabels[item.source_type]}</span>{item.source_url ? <a className="text-sm font-medium text-cyan-300 underline underline-offset-4" href={item.source_url} rel="noreferrer" target="_blank">{item.source_title}</a> : <p className="text-sm font-medium">{item.source_title}</p>}</div>{item.quote ? <p className="mt-2 text-sm leading-6 text-slate-300">{item.quote}</p> : null}{item.source_type === "model_inference" ? <p className="mt-2 text-xs text-amber-200">模型推断不构成事实证据，需进一步验证。</p> : null}</article>)}{evidence.length === 0 ? <p className="text-sm text-slate-500">暂无可展示的证据来源。</p> : null}</div></section>; }
