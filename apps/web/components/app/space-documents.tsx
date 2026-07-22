"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { StatusStamp } from "@/components/evidence/status-stamp";
import { getCurrentUser } from "@/lib/auth";
import { ApiClientError } from "@/lib/api-client";
import {
  deleteDocument,
  listDocuments,
  type DocumentRecord,
  uploadDocument,
} from "@/lib/documents";
import { indexDocument } from "@/lib/retrieval";

const maximumFileSize = 20 * 1024 * 1024;

function errorMessage(error: unknown): string {
  return error instanceof ApiClientError ? error.message : "网络请求失败，请稍后重试";
}

export function SpaceDocuments({ spaceId }: { spaceId: string }) {
  const { replace } = useRouter();
  const [documents, setDocuments] = useState<DocumentRecord[] | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const requestVersion = useRef(0);

  const loadDocuments = useCallback(async () => {
    const request = ++requestVersion.current;
    setError(null);
    try {
      await getCurrentUser();
      const nextDocuments = await listDocuments(spaceId);
      if (request === requestVersion.current) setDocuments(nextDocuments);
    } catch (caughtError) {
      if (request !== requestVersion.current) return;
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") {
        replace("/login");
        return;
      }
      setError(errorMessage(caughtError));
    }
  }, [replace, spaceId]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => { if (active) return loadDocuments(); });
    return () => { active = false; requestVersion.current += 1; };
  }, [loadDocuments]);

  const onUpload = async () => {
    if (!selectedFile || isSubmitting) return;
    if (selectedFile.size > maximumFileSize) {
      setError("单个文件不能超过 20MB");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await uploadDocument(spaceId, selectedFile);
      setSelectedFile(null);
      await loadDocuments();
    } catch (caughtError) {
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") {
        replace("/login");
        return;
      }
      setError(errorMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  };

  const onDelete = async (document: DocumentRecord) => {
    if (isSubmitting) return;
    setError(null);
    setIsSubmitting(true);
    try {
      await deleteDocument(document.id);
      await loadDocuments();
    } catch (caughtError) {
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") {
        replace("/login");
        return;
      }
      setError(errorMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  };

  const onIndex = async (document: DocumentRecord) => {
    if (isSubmitting || document.status === "processing") return;
    setError(null);
    setIsSubmitting(true);
    try {
      await indexDocument(document.id);
      await loadDocuments();
    } catch (caughtError) {
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") {
        replace("/login");
        return;
      }
      setError(errorMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  };

  return <div className="max-w-4xl">
    <div className="border-b border-border pb-6"><p className="text-sm font-medium text-primary">资料档案</p><h1 className="mt-2 text-3xl font-semibold tracking-tight text-foreground">文档管理</h1><p className="mt-2 text-sm leading-6 text-muted-foreground">为竞品分析沉淀可检索的原始资料。支持 PDF、DOCX、TXT 和 Markdown，单个文件最大 20MB。</p></div>
    <div className="mt-6 flex flex-wrap items-center gap-3 rounded-lg border border-border bg-card p-5 shadow-sm">
      <input aria-label="选择文档" accept=".pdf,.docx,.txt,.md" disabled={isSubmitting} onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} type="file" />
      <Button disabled={!selectedFile || isSubmitting} onClick={onUpload} type="button">{isSubmitting ? "处理中…" : "上传文档"}</Button>
    </div>
    {error && <p className="mt-4 text-sm text-destructive" role="alert">{error}</p>}
    <section className="mt-6" aria-labelledby="document-archive-heading">
      <div className="mb-3 flex items-center justify-between"><h2 className="text-base font-semibold text-foreground" id="document-archive-heading">已归档资料</h2>{documents && <span className="text-xs text-muted-foreground">{documents.length} 份文档</span>}</div>
      {documents === null && !error && <p className="text-sm text-muted-foreground">正在加载文档…</p>}
      {documents?.length === 0 && <p className="rounded-lg border border-dashed border-border bg-card p-8 text-center text-muted-foreground">还没有上传文档</p>}
      {documents && documents.length > 0 && <ul className="space-y-3">{documents.map((document) => <li className="flex flex-col gap-4 rounded-lg border border-border bg-card p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between" key={document.id}><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><p className="truncate font-medium text-foreground">{document.filename}</p><StatusStamp status={document.status} /></div><p className="mt-2 text-sm text-muted-foreground">{document.file_type.toUpperCase()} · {document.file_size} B · {new Date(document.created_at).toLocaleString("zh-CN")}</p>{document.error_message && <p className="mt-2 text-sm text-destructive">{document.error_message}</p>}</div><Button aria-label={`删除 ${document.filename}`} disabled={isSubmitting} onClick={() => void onDelete(document)} type="button" variant="outline">删除</Button></li>)}</ul>}
    </section>
    {documents && documents.length > 0 && <div className="mt-3 flex flex-wrap gap-2">
      {documents.map((document) => {
        if (document.status === "indexed") return null;
        const isProcessing = document.status === "processing";
        const label = isProcessing ? "正在处理" : document.status === "failed" ? "重新索引" : "开始索引";
        return <Button aria-label={`${label} ${document.filename}`} disabled={isSubmitting || isProcessing} key={`index-${document.id}`} onClick={() => void onIndex(document)} type="button" variant="outline">{label}</Button>;
      })}
    </div>}
  </div>;
}
