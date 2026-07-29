import type { AnalysisAgentRun } from "@/lib/analysis-tasks";

const agentLabels: Record<AnalysisAgentRun["agent_key"], string> = {
  evidence_collection: "证据收集",
  quality_check: "质量检查",
  model_analysis: "模型分析",
  report_generation: "报告生成",
};

const statusLabels: Record<AnalysisAgentRun["status"], string> = {
  queued: "等待执行",
  running: "执行中",
  completed: "已完成",
  failed: "执行失败",
  skipped: "未执行",
};

const agentOrder: AnalysisAgentRun["agent_key"][] = ["evidence_collection", "quality_check", "model_analysis", "report_generation"];

function formatTime(value: string | null) {
  if (!value) return null;
  return new Intl.DateTimeFormat("zh-CN", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

export function AnalysisAgentRunHistory({ agentRuns }: { agentRuns: AnalysisAgentRun[] }) {
  if (agentRuns.length === 0) return null;

  const attempts = [...new Set(agentRuns.map((run) => run.attempt))].sort((left, right) => right - left);

  return (
    <section className="mt-6 border-t border-border pt-5" aria-label="Agent 运行记录">
      <h2 className="text-sm font-medium">Agent 运行记录</h2>
      <div className="mt-4 space-y-4">
        {attempts.map((attempt) => {
          const runs = agentRuns.filter((run) => run.attempt === attempt).sort((left, right) => agentOrder.indexOf(left.agent_key) - agentOrder.indexOf(right.agent_key));
          return (
            <article className="rounded-xl border border-border p-4" key={attempt}>
              <h3 className="text-sm font-medium">第 {attempt} 次运行</h3>
              <ol className="mt-3 space-y-3">
                {runs.map((run) => {
                  const time = formatTime(run.completed_at ?? run.started_at);
                  return (
                    <li className="rounded-lg bg-muted/60 p-3 text-sm" key={run.agent_key}>
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="font-medium">{agentLabels[run.agent_key]}</p>
                        <span className="text-muted-foreground">{statusLabels[run.status]}</span>
                      </div>
                      {time && <p className="mt-1 text-xs text-muted-foreground">{time}</p>}
                      {run.status === "failed" && run.failure_reason && <p className="mt-2 text-sm text-destructive">{run.failure_reason}</p>}
                    </li>
                  );
                })}
              </ol>
            </article>
          );
        })}
      </div>
    </section>
  );
}
