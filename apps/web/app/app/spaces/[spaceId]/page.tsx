"use client";

import { useParams } from "next/navigation";
import Link from "next/link";

import { SpaceDocuments } from "@/components/app/space-documents";
import { SpaceRetrieval } from "@/components/app/space-retrieval";
import { AppShell } from "@/components/app-shell";

export default function SpaceDocumentsPage() {
  const { spaceId } = useParams<{ spaceId: string }>();

  return <AppShell><div className="mb-8 rounded-2xl border border-slate-700 bg-slate-950 p-6 text-slate-100 shadow-sm"><p className="text-sm font-medium text-cyan-300">竞争情报工作台</p><h1 className="mt-1 text-2xl font-semibold tracking-tight">从资料档案到可引用的竞品洞察</h1><p className="mt-2 max-w-2xl text-sm text-slate-300">上传并索引资料后，可在同一空间检索来源片段，再发起有据可查的分析任务。</p><Link className="mt-5 inline-block rounded-lg bg-cyan-400 px-4 py-2 text-sm font-medium text-slate-950 transition-colors hover:bg-cyan-300" href={`/app/spaces/${spaceId}/tasks/new`}>新建分析任务</Link></div><SpaceDocuments spaceId={spaceId} /><SpaceRetrieval spaceId={spaceId} /></AppShell>;
}
