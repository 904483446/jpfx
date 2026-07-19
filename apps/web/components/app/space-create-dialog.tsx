"use client";

import { type FormEvent, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/lib/api-client";
import { createSpace, type CreateSpaceInput, type Space } from "@/lib/spaces";

const emptyValues: CreateSpaceInput = { name: "", industry: "", productDirection: "", description: "" };

export function SpaceCreateDialog({ open, onOpenChange, onCreated }: { open: boolean; onOpenChange: (open: boolean) => void; onCreated: (space: Space) => void; }) {
  const [values, setValues] = useState(emptyValues);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const submissionLock = useRef(false);
  const close = () => { if (isSubmitting) return; setValues(emptyValues); setError(null); onOpenChange(false); };
  useEffect(() => { if (!open) return; const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") close(); }; window.addEventListener("keydown", onKeyDown); return () => window.removeEventListener("keydown", onKeyDown); });
  if (!open) return null;
  const update = (field: keyof CreateSpaceInput, value: string) => setValues((current) => ({ ...current, [field]: value }));
  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); if (submissionLock.current || isSubmitting) return;
    if (!values.name.trim()) { setError("请填写产品空间名称"); return; }
    submissionLock.current = true; setError(null); setIsSubmitting(true);
    try { const space = await createSpace(values); if (!space) { setError("网络请求失败，请稍后重试"); return; } close(); onCreated(space); }
    catch (caughtError) { setError(caughtError instanceof ApiClientError ? caughtError.message : "网络请求失败，请稍后重试"); }
    finally { submissionLock.current = false; setIsSubmitting(false); }
  };
  return <div className="fixed inset-0 z-50 grid place-items-center bg-foreground/35 p-4" onMouseDown={(event) => { if (event.target === event.currentTarget) close(); }}>
    <section aria-labelledby="create-space-title" aria-modal="true" className="w-full max-w-lg border border-border bg-card p-6 shadow-2xl" role="dialog">
      <div className="flex items-start justify-between gap-4"><div><p className="font-mono text-[0.68rem] tracking-[0.14em] text-muted-foreground">新建档案</p><h2 className="mt-2 text-xl font-semibold" id="create-space-title">新建产品空间</h2><p className="mt-1 text-sm text-muted-foreground">创建后可在后续任务中管理资料与分析。</p></div><Button aria-label="关闭新建产品空间弹窗" disabled={isSubmitting} onClick={close} type="button" variant="ghost">关闭</Button></div>
      <form className="mt-6 space-y-4" noValidate onSubmit={onSubmit}>
        <div className="space-y-2"><label htmlFor="space-name">空间名称</label><Input id="space-name" disabled={isSubmitting} onChange={(event) => update("name", event.target.value)} value={values.name} /></div>
        <div className="space-y-2"><label htmlFor="space-industry">行业</label><Input id="space-industry" disabled={isSubmitting} onChange={(event) => update("industry", event.target.value)} value={values.industry} /></div>
        <div className="space-y-2"><label htmlFor="space-product-direction">产品方向</label><Input id="space-product-direction" disabled={isSubmitting} onChange={(event) => update("productDirection", event.target.value)} value={values.productDirection} /></div>
        <div className="space-y-2"><label htmlFor="space-description">描述</label><textarea className="min-h-24 w-full border border-input bg-transparent p-2" disabled={isSubmitting} id="space-description" onChange={(event) => update("description", event.target.value)} value={values.description} /></div>
        {error && <p className="text-sm text-destructive" role="alert">{error}</p>}
        <div className="flex justify-end gap-2"><Button disabled={isSubmitting} onClick={close} type="button" variant="outline">取消</Button><Button disabled={isSubmitting} type="submit">{isSubmitting ? "创建中…" : "创建产品空间"}</Button></div>
      </form>
    </section>
  </div>;
}
