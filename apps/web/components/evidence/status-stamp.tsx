export type EvidenceStatus =
  | "uploaded"
  | "processing"
  | "indexed"
  | "failed"
  | "draft"
  | "queued"
  | "running"
  | "completed";

const statusMeta: Record<EvidenceStatus, { label: string; tone: string }> = {
  uploaded: { label: "已上传", tone: "bg-stone-200 text-stone-700 dark:bg-stone-700 dark:text-stone-100" },
  processing: { label: "处理中", tone: "bg-amber-100 text-amber-800 dark:bg-amber-900/70 dark:text-amber-100" },
  indexed: { label: "已索引", tone: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/70 dark:text-emerald-100" },
  failed: { label: "失败", tone: "bg-red-100 text-red-800 dark:bg-red-900/70 dark:text-red-100" },
  draft: { label: "草稿", tone: "bg-stone-200 text-stone-700 dark:bg-stone-700 dark:text-stone-100" },
  queued: { label: "排队中", tone: "bg-sky-100 text-sky-800 dark:bg-sky-900/70 dark:text-sky-100" },
  running: { label: "运行中", tone: "bg-amber-100 text-amber-800 dark:bg-amber-900/70 dark:text-amber-100" },
  completed: { label: "已完成", tone: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/70 dark:text-emerald-100" },
};

export function StatusStamp({ status }: { status: EvidenceStatus }) {
  const { label, tone } = statusMeta[status];

  return (
    <span
      aria-label={`文档状态：${label}`}
      role="status"
      className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${tone}`}
    >
      {label}
    </span>
  );
}
