"use client";

import { useParams } from "next/navigation";
import Link from "next/link";

import { SpaceDocuments } from "@/components/app/space-documents";
import { SpaceRetrieval } from "@/components/app/space-retrieval";
import { AppShell } from "@/components/app-shell";

export default function SpaceDocumentsPage() {
  const { spaceId } = useParams<{ spaceId: string }>();

  return <AppShell><div className="mb-6 rounded-2xl border border-slate-700 bg-slate-900 p-5 text-slate-100"><p className="text-sm text-cyan-300">竞争情报工作台</p><h1 className="mt-1 text-xl font-semibold">从空间资料开始竞品分析</h1><Link className="mt-4 inline-block rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-slate-950" href={`/app/spaces/${spaceId}/tasks/new`}>新建分析任务</Link></div><SpaceDocuments spaceId={spaceId} /><SpaceRetrieval spaceId={spaceId} /></AppShell>;
}
