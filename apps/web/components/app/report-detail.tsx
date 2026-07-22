"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ApiClientError } from "@/lib/api-client";
import { ReportArchive } from "@/components/app/report-archive";
import { downloadReport, getReport, getReportEvidence, type CompetitorReport, type ReportEvidence } from "@/lib/reports";

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

  return <section className="mx-auto max-w-6xl text-foreground">
    <div className="rounded-3xl border border-border bg-background p-6 shadow-2xl shadow-black/5 md:p-8">
      <div className="flex flex-col justify-between gap-5 border-b border-border pb-6 md:flex-row md:items-start"><div><p className="text-sm font-medium tracking-[0.16em] text-cyan-700 dark:text-cyan-300">报告档案</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">{report?.title ?? "正在加载报告…"}</h1>{report ? <p className="mt-3 text-sm text-muted-foreground">生成于 {new Date(report.created_at).toLocaleString("zh-CN")}</p> : null}</div><div className="flex gap-3"><Button disabled={!report || downloading !== null} onClick={() => void exportFile("pdf")} type="button">{downloading === "pdf" ? "正在下载…" : "下载 PDF"}</Button><Button disabled={!report || downloading !== null} onClick={() => void exportFile("docx")} type="button" variant="outline">{downloading === "docx" ? "正在下载…" : "下载 DOCX"}</Button></div></div>
      {error ? <p className="mt-5 text-sm text-red-300" role="alert">{error}</p> : null}
      {report ? <ReportArchive report={report} evidence={evidence} /> : null}
    </div>
  </section>;
}

