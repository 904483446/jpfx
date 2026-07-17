"use client";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app-shell";
import { AnalysisTaskStatus } from "@/components/app/analysis-task-status";
import { CandidateConfirmation } from "@/components/app/candidate-confirmation";
export default function AnalysisTaskPage() { const { taskId } = useParams<{ taskId: string }>(); return <AppShell><div className="mx-auto max-w-4xl"><AnalysisTaskStatus taskId={taskId} /><CandidateConfirmation taskId={taskId} /></div></AppShell>; }
