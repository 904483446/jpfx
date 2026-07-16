"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
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

const statusLabels = {
  uploaded: "已上传",
  processing: "处理中",
  indexed: "已索引",
  failed: "处理失败",
} as const;

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

  return <div className="max-w-3xl">
    <div><p className="text-sm font-medium text-[#14b8a6]">产品空间</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">文档管理</h1><p className="mt-2 text-sm text-slate-500">支持 PDF、DOCX、TXT 和 Markdown，单个文件最大 20MB。</p></div>
    <div className="mt-6 flex flex-wrap items-center gap-3 rounded-2xl border border-slate-200 bg-white p-5">
      <input aria-label="选择文档" accept=".pdf,.docx,.txt,.md" disabled={isSubmitting} onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} type="file" />
      <Button disabled={!selectedFile || isSubmitting} onClick={onUpload} type="button">{isSubmitting ? "处理中…" : "上传文档"}</Button>
    </div>
    {error && <p className="mt-4 text-sm text-red-600" role="alert">{error}</p>}
    <section className="mt-6">
      {documents === null && !error && <p className="text-sm text-slate-500">正在加载文档…</p>}
      {documents?.length === 0 && <p className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">还没有上传文档</p>}
      {documents && documents.length > 0 && <ul className="space-y-3">{documents.map((document) => <li className="flex items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-4" key={document.id}><div><p className="font-medium">{document.filename}</p><p className="mt-1 text-sm text-slate-500">{document.file_type.toUpperCase()} · {document.file_size} B · {new Date(document.created_at).toLocaleString("zh-CN")} · {statusLabels[document.status]}</p>{document.error_message && <p className="mt-1 text-sm text-red-600">{document.error_message}</p>}</div><Button aria-label={`删除 ${document.filename}`} disabled={isSubmitting} onClick={() => void onDelete(document)} type="button" variant="outline">删除</Button></li>)}</ul>}
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
