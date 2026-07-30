"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { type CurrentUser } from "@/lib/auth";
import { ApiClientError } from "@/lib/api-client";
import { listSpaces, type Space } from "@/lib/spaces";
import { SpaceCreateDialog } from "./space-create-dialog";

export function DashboardSpaces({ user }: { user: CurrentUser }) {
  const { replace } = useRouter();
  const [spaces, setSpaces] = useState<Space[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const requestVersion = useRef(0);
  const loadSpaces = useCallback(async () => {
    const request = ++requestVersion.current; setError(null); setSpaces(null);
    try { const nextSpaces = await listSpaces(); if (request === requestVersion.current) setSpaces(nextSpaces); }
    catch (caughtError) { if (request !== requestVersion.current) return; if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") { replace("/login"); return; } setError(caughtError instanceof ApiClientError ? caughtError.message : "网络请求失败，请稍后重试"); }
  }, [replace]);
  useEffect(() => { let active = true; void Promise.resolve().then(() => { if (active) return loadSpaces(); }); return () => { active = false; requestVersion.current += 1; }; }, [loadSpaces]);
  return <div className="max-w-6xl">
    <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border pb-6"><div><p className="font-mono text-[0.68rem] tracking-[0.16em] text-muted-foreground">工作台 / 01</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">研究总览</h1><p className="mt-2 text-sm text-muted-foreground">{user.display_name}，从产品空间开始组织资料、任务与可核查结论。</p></div><Button onClick={() => setIsDialogOpen(true)} type="button">新建产品空间</Button></div>
    <div className="mt-8">
      {spaces === null && !error && <div aria-busy="true" className="grid gap-4 md:grid-cols-2" data-testid="space-list-skeleton"><div className="h-44 animate-pulse border border-border bg-card" /><div className="h-44 animate-pulse border border-border bg-card" /><span className="sr-only">正在加载产品空间…</span></div>}
      {error && <div className="space-y-4"><p className="text-sm text-destructive" role="alert">{error}</p><Button onClick={loadSpaces} type="button" variant="outline">重试</Button></div>}
      {spaces?.length === 0 && <div className="border border-dashed border-border bg-card p-8 text-center sm:p-12"><p className="font-mono text-[0.68rem] tracking-[0.16em] text-muted-foreground">空白档案</p><h2 className="mt-3 text-xl font-semibold">还没有产品空间</h2><p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">从一个产品空间开始，归集资料、分析任务与可复核的结论。</p><Button className="mt-5" onClick={() => setIsDialogOpen(true)} type="button">创建第一个产品空间</Button></div>}
      {spaces && spaces.length > 0 && <div className="grid gap-4 md:grid-cols-2">{spaces.map((space) => <Link aria-label={space.name} className="block border border-border bg-card p-5 transition-colors hover:border-foreground" href={"/app/spaces/" + space.id} key={space.id}><p className="font-mono text-[0.68rem] tracking-[0.12em] text-muted-foreground">产品空间</p><h2 className="mt-2 font-semibold">{space.name}</h2>{space.industry && <p className="mt-3 text-sm text-muted-foreground">{space.industry}</p>}{space.product_direction && <p className="mt-1 text-sm text-muted-foreground">{space.product_direction}</p>}{space.description && <p className="mt-3 text-sm text-foreground/80">{space.description}</p>}</Link>)}</div>}
    </div>
    <SpaceCreateDialog onCreated={(space) => replace("/app/spaces/" + space.id)} onOpenChange={setIsDialogOpen} open={isDialogOpen} />
  </div>;
}
