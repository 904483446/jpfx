"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { AnalysisAgentRunHistory } from "@/components/app/analysis-agent-run-history";
import { ApiClientError } from "@/lib/api-client";
import { getAnalysisTask, retryAnalysisTask, type AnalysisTask } from "@/lib/analysis-tasks";

const statusLabels: Record<AnalysisTask["status"], string> = { draft: "待确认", queued: "等待执行", running: "分析中", completed: "已完成", failed: "分析失败" };
const stages = ["任务已创建", "候选确认", "分析准备", "证据采集", "证据质量检查", "模型调用", "报告生成"];
const backendStageLabels: Record<string, string> = {
  retrieving_private_knowledge: "私有知识检索",
  quality_checking: "证据质量检查",
  analyzing: "正在模型分析",
};

function stagePosition(task: AnalysisTask) {
  if (task.status === "completed") return stages.length - 1;
  if (task.status === "draft") return 1;
  if (task.status === "queued") return 2;
  if (task.status === "failed") return null;
  const stage = task.stage ?? "";
  if (stage === "retrieving_private_knowledge") return 3;
  if (stage === "quality_checking") return 4;
  if (stage === "analyzing") return 5;
  if (stage.includes("报告")) return 6;
  if (stage.includes("模型")) return 5;
  if (stage.includes("证据") || stage.includes("检索")) return 3;
  return 2;
}

function stageLabel(task: AnalysisTask, activeStage: number | null) {
  if (task.status === "failed") return "任务未完成，请重试";
  const stage = task.stage ?? "";
  return backendStageLabels[stage] ?? (stage || stages[activeStage ?? 0]);
}

export function AnalysisTaskStatus({ taskId }: { taskId: string }) {
  const { replace } = useRouter();
  const [task, setTask] = useState<AnalysisTask | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stop = () => { if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; } };
  const load = useCallback(async () => {
    try { const next = await getAnalysisTask(taskId); if (!next) return; setTask(next); if (next.status === "completed" || next.status === "failed") stop(); }
    catch (caught) { if (caught instanceof ApiClientError && caught.code === "UNAUTHORIZED") { stop(); replace("/login"); return; } setError(caught instanceof ApiClientError ? caught.message : "网络请求失败，请稍后重试"); }
  }, [replace, taskId]);
  useEffect(() => { void Promise.resolve().then(load); intervalRef.current = setInterval(() => void load(), 2000); return stop; }, [load]);
  const retry = async () => {
    if (isRetrying) return;
    setIsRetrying(true); setError(null);
    try { const next = await retryAnalysisTask(taskId); if (next) { setTask(next); stop(); intervalRef.current = setInterval(() => void load(), 2000); } }
    catch (caught) { if (caught instanceof ApiClientError && caught.code === "UNAUTHORIZED") replace("/login"); else setError(caught instanceof ApiClientError ? caught.message : "网络请求失败，请稍后重试"); }
    finally { setIsRetrying(false); }
  };
  const activeStage = task ? stagePosition(task) : 0;
  return <section className="rounded-2xl border border-border bg-card p-6 text-card-foreground shadow-sm">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div><p className="text-sm font-medium text-primary">分析工作台</p><h1 className="mt-2 text-2xl font-semibold">{task?.title ?? "正在载入任务…"}</h1></div>
      {task && <p className="rounded-full bg-muted px-3 py-1 text-sm font-medium">{statusLabels[task.status]}</p>}
    </div>
      {task && <><div className="mt-6 border-t border-border pt-5"><p className="text-sm font-medium">分析进度</p><ol className="mt-4 grid gap-3 sm:grid-cols-3">{stages.map((stage, index) => <li className="flex items-center gap-2 text-sm" key={stage}><span className={`grid size-6 shrink-0 place-items-center rounded-full text-xs ${activeStage !== null && index <= activeStage ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>{index + 1}</span><span className={index === activeStage ? "font-medium" : "text-muted-foreground"}>{stage}</span></li>)}</ol></div>
      <div className="mt-5 rounded-xl bg-muted/60 p-4 text-sm"><p className="font-medium">{task.status === "failed" ? "失败阶段" : "当前阶段"}</p><p className="mt-1 text-muted-foreground">{stageLabel(task, activeStage)}</p></div>
      {task.status === "completed" && <p className="mt-4 text-sm text-emerald-700 dark:text-emerald-300">报告已生成，可继续查看分析结论。</p>}
      {task.status === "failed" && <Button className="mt-4" disabled={isRetrying} onClick={() => void retry()} type="button">{isRetrying ? "正在重新分析…" : "重新分析"}</Button>}
      <AnalysisAgentRunHistory agentRuns={task.agent_runs} />
    </>}
    {error && <p className="mt-4 text-sm text-destructive" role="alert">{error}</p>}
  </section>;
}
