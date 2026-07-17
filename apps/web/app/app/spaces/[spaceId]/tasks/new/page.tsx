"use client";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app-shell";
import { AnalysisTaskCreate } from "@/components/app/analysis-task-create";
export default function AnalysisTaskCreatePage() { const { spaceId } = useParams<{ spaceId: string }>(); return <AppShell><AnalysisTaskCreate spaceId={spaceId} /></AppShell>; }
