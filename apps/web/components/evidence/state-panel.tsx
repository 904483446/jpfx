import type { ReactNode } from "react";

export type StatePanelKind = "empty" | "loading" | "error";

type StatePanelProps = {
  kind: StatePanelKind;
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
};

const kindStyles: Record<StatePanelKind, string> = {
  empty: "border-border bg-card",
  loading: "border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/40",
  error: "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/40",
};

export function StatePanel({ kind, title, description, action }: StatePanelProps) {
  return (
    <section className={`rounded-lg border p-6 text-center ${kindStyles[kind]}`}>
      <h2 className="text-base font-semibold text-foreground">{title}</h2>
      {description ? <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p> : null}
      {action ? <div className="mt-4 flex justify-center">{action}</div> : null}
    </section>
  );
}
