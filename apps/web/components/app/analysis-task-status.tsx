"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ApiClientError } from "@/lib/api-client";
import { getAnalysisTask, retryAnalysisTask, type AnalysisTask } from "@/lib/analysis-tasks";

const labels: Record<AnalysisTask["status"], string> = { draft: "Waiting for confirmation", queued: "Queued", running: "Analysing", completed: "Completed", failed: "Failed" };

export function AnalysisTaskStatus({ taskId }: { taskId: string }) {
  const { replace } = useRouter();
  const [task, setTask] = useState<AnalysisTask | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stop = () => { if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; } };
  const load = useCallback(async () => {
    try { const next = await getAnalysisTask(taskId); if (!next) return; setTask(next); if (next.status === "completed" || next.status === "failed") stop(); }
    catch (caught) { if (caught instanceof ApiClientError && caught.code === "UNAUTHORIZED") { stop(); replace("/login"); return; } setError(caught instanceof ApiClientError ? caught.message : "Network request failed. Please try again."); }
  }, [replace, taskId]);
  useEffect(() => { void Promise.resolve().then(load); intervalRef.current = setInterval(() => void load(), 2000); return stop; }, [load]);
  const retry = async () => {
    if (isRetrying) return; setIsRetrying(true); setError(null);
    try { const next = await retryAnalysisTask(taskId); if (next) { setTask(next); stop(); intervalRef.current = setInterval(() => void load(), 2000); } }
    catch (caught) { if (caught instanceof ApiClientError && caught.code === "UNAUTHORIZED") replace("/login"); else setError(caught instanceof ApiClientError ? caught.message : "Network request failed. Please try again."); }
    finally { setIsRetrying(false); }
  };
  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-900 p-6 text-slate-100">
      <p className="text-sm font-medium text-cyan-300">Analysis task</p>
      <h1 className="mt-2 text-2xl font-semibold">{task?.title ?? "Loading task..."}</h1>
      {task ? <>
        <p className="mt-4 inline-flex rounded-full bg-slate-800 px-3 py-1 text-sm">{labels[task.status]}</p>
        {task.stage ? <p className="mt-3 text-sm text-slate-400">Current stage: {task.stage}</p> : null}
        {task.status === "completed" ? <p className="mt-3 text-sm text-emerald-300">Report generated.</p> : null}
        {task.status === "failed" ? <Button className="mt-4" disabled={isRetrying} onClick={() => void retry()} type="button">{isRetrying ? "Retrying..." : "Retry analysis"}</Button> : null}
      </> : null}
      {error ? <p className="mt-4 text-sm text-red-300" role="alert">{error}</p> : null}
    </section>
  );
}
