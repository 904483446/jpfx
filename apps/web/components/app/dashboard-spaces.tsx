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
    const request = ++requestVersion.current;
    setError(null); setSpaces(null);
    try { const nextSpaces = await listSpaces(); if (request === requestVersion.current) setSpaces(nextSpaces); }
    catch (caughtError) {
      if (request !== requestVersion.current) return;
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") { replace("/login"); return; }
      setError(caughtError instanceof ApiClientError ? caughtError.message : "网络请求失败，请稍后重试");
    }
  }, [replace]);
  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => { if (active) return loadSpaces(); });
    return () => { active = false; requestVersion.current += 1; };
  }, [loadSpaces]);
  return <div className="max-w-5xl">
    <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-sm font-medium text-[#14b8a6]">工作台</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">欢迎回来，{user.display_name}</h1><p className="mt-2 text-sm text-slate-500">{user.email}</p></div><Button onClick={() => setIsDialogOpen(true)} type="button">新建产品空间</Button></div>
    <div className="mt-8">
      {spaces === null && !error && <p className="text-sm text-slate-500">正在加载产品空间…</p>}
      {error && <div className="space-y-4"><p className="text-sm text-red-600" role="alert">{error}</p><Button onClick={loadSpaces} type="button" variant="outline">重试</Button></div>}
      {spaces?.length === 0 && <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center"><p className="text-slate-600">还没有产品空间</p><Button className="mt-4" onClick={() => setIsDialogOpen(true)} type="button">新建产品空间</Button></div>}
      {spaces && spaces.length > 0 && <div className="grid gap-4 md:grid-cols-2">{spaces.map((space) => <Link aria-label={space.name} className="rounded-2xl border border-slate-200 bg-white p-5 hover:border-[#1677ff]" href={"/app/spaces/" + space.id} key={space.id}><h2 className="font-semibold">{space.name}</h2>{space.industry && <p className="mt-2 text-sm text-slate-500">{space.industry}</p>}{space.product_direction && <p className="mt-1 text-sm text-slate-500">{space.product_direction}</p>}{space.description && <p className="mt-3 text-sm text-slate-600">{space.description}</p>}</Link>)}</div>}
    </div>
    <SpaceCreateDialog onCreated={(space) => replace("/app/spaces/" + space.id)} onOpenChange={setIsDialogOpen} open={isDialogOpen} />
  </div>;
}
