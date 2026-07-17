"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/app-shell";
import { ReportDetail } from "@/components/app/report-detail";

export default function ReportDetailPage() {
  const { reportId } = useParams<{ reportId: string }>();
  return <AppShell><ReportDetail reportId={reportId} /></AppShell>;
}
