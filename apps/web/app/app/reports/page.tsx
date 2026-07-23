import { ReportArchiveList } from "@/components/app/report-archive-list";
import { AppShell } from "@/components/app-shell";

export default function ReportsPage() {
  return <AppShell><section className="mx-auto max-w-6xl"><p className="font-mono text-[0.68rem] tracking-[0.16em] text-primary">报告中心</p><h1 className="mt-2 text-3xl font-semibold tracking-tight text-foreground">研究归档</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">查看已完成的竞品研究，并继续进入报告详情核对证据和导出交付文件。</p><ReportArchiveList /></section></AppShell>;
}
