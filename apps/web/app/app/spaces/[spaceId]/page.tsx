"use client";

import { useParams } from "next/navigation";
import Link from "next/link";

import { SpaceDocuments } from "@/components/app/space-documents";
import { SpaceRetrieval } from "@/components/app/space-retrieval";
import { AppShell } from "@/components/app-shell";

export default function SpaceDocumentsPage() {
  const { spaceId } = useParams<{ spaceId: string }>();

  return <AppShell><div className="mb-8 rounded-2xl border border-border bg-card p-6 text-card-foreground"><p className="text-sm font-medium text-primary">竞争情报工作台</p><h1 className="mt-1 text-2xl font-semibold tracking-tight">从资料档案到可引用的竞品洞察</h1><p className="mt-2 max-w-2xl text-sm text-muted-foreground">上传并索引资料后，可在同一空间检索来源片段，再发起有据可查的分析任务。</p><Link className="mt-5 inline-block rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/85" href={`/app/spaces/${spaceId}/tasks/new`}>新建分析任务</Link></div><SpaceDocuments spaceId={spaceId} /><SpaceRetrieval spaceId={spaceId} /></AppShell>;
}
