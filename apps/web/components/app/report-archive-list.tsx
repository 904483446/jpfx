"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ApiClientError } from "@/lib/api-client";
import { listReports, type CompetitorReport } from "@/lib/reports";

export function ReportArchiveList() {
  const { replace } = useRouter();
  const [reports, setReports] = useState<CompetitorReport[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      setReports((await listReports()) ?? []);
    } catch (caught) {
      if (caught instanceof ApiClientError && caught.code === "UNAUTHORIZED") {
        replace("/login");
        return;
      }
      setError(caught instanceof ApiClientError ? caught.message : "加载报告失败，请稍后重试。");
    }
  }, [replace]);

  useEffect(() => {
    void Promise.resolve().then(load);
  }, [load]);

  if (error) {
    return <div className="mt-8 rounded-xl border border-destructive/30 bg-destructive/5 p-5"><p className="text-sm text-destructive" role="alert">{error}</p><Button className="mt-4" onClick={() => void load()} type="button" variant="outline">重试</Button></div>;
  }

  if (reports === null) return <p className="mt-8 text-sm text-muted-foreground">正在加载归档报告…</p>;
  if (reports.length === 0) return <p className="mt-8 rounded-xl border border-dashed border-border bg-card p-8 text-center text-muted-foreground">还没有归档报告</p>;

  return <ul className="mt-8 space-y-3" aria-label="归档报告列表">
    {reports.map((report) => <li className="rounded-xl border border-border bg-card p-5 shadow-sm" key={report.id}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"><div className="min-w-0"><p className="font-mono text-[0.68rem] tracking-[0.16em] text-primary">REPORT · {String(report.version).padStart(2, "0")}</p><Link className="mt-2 block truncate text-lg font-semibold text-foreground underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" href={`/app/reports/${report.id}`}>{report.title}</Link><p className="mt-2 text-sm text-muted-foreground">生成于 {new Date(report.created_at).toLocaleString("zh-CN")} · 空间 {report.space_id}</p></div><Link className="shrink-0 text-sm font-medium text-primary underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" href={`/app/reports/${report.id}`}>查看报告</Link></div>
    </li>)}
  </ul>;
}
