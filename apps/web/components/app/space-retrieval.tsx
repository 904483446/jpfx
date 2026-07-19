"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { getCurrentUser } from "@/lib/auth";
import { ApiClientError } from "@/lib/api-client";
import { searchSpaceDocuments, type RetrievalResult } from "@/lib/retrieval";

function errorMessage(error: unknown): string {
  return error instanceof ApiClientError ? error.message : "网络请求失败，请稍后重试";
}

export function SpaceRetrieval({ spaceId }: { spaceId: string }) {
  const { replace } = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<RetrievalResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    void getCurrentUser().catch((caughtError: unknown) => {
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") replace("/login");
    });
  }, [replace]);

  const onSearch = async () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery || isSearching) return;
    setError(null);
    setIsSearching(true);
    try {
      const response = await searchSpaceDocuments(spaceId, trimmedQuery);
      setResults(response?.results ?? []);
    } catch (caughtError) {
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") {
        replace("/login");
        return;
      }
      setError(errorMessage(caughtError));
    } finally {
      setIsSearching(false);
    }
  };

  return <section className="mt-10 max-w-4xl border-t border-slate-200 pt-8 dark:border-slate-700" aria-labelledby="space-retrieval-heading">
    <p className="text-sm font-medium text-[#14b8a6]">检索与引用</p>
    <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-slate-50" id="space-retrieval-heading">空间检索</h2>
    <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">检索当前空间中已索引文档的相关片段，并保留可追溯的引用来源。</p>
    <div className="mt-4 flex flex-wrap gap-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <label className="sr-only" htmlFor="retrieval-query">检索问题</label>
      <input aria-label="检索问题" className="min-w-56 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm" disabled={isSearching} id="retrieval-query" onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void onSearch(); }} placeholder="例如：目标用户是谁？" value={query} />
      <Button disabled={!query.trim() || isSearching} onClick={() => void onSearch()} type="button">{isSearching ? "检索中…" : "检索"}</Button>
    </div>
    {error && <p className="mt-4 text-sm text-red-600" role="alert">{error}</p>}
    {results?.length === 0 && <p className="mt-4 rounded-2xl border border-dashed border-slate-300 bg-white p-5 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">没有找到相关文档片段</p>}
    {results && results.length > 0 && <ol className="mt-4 space-y-3">{results.map((result) => <li className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900" key={`${result.filename}-${result.chunk_index}-${result.content}`}><div className="mb-3 flex items-center justify-between gap-3"><p className="text-xs font-medium tracking-wide text-[#0f766e] dark:text-teal-300">引用片段 {String(result.chunk_index + 1).padStart(2, "0")}</p><span className="rounded-full bg-teal-50 px-2 py-1 text-xs font-medium text-teal-800 dark:bg-teal-950/70 dark:text-teal-200">相似度 {result.similarity.toFixed(2)}</span></div><p className="whitespace-pre-wrap text-sm leading-6 text-slate-700 dark:text-slate-200">{result.content}</p><p className="mt-4 border-t border-slate-100 pt-3 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">引用来源：{result.filename} · 片段 {result.chunk_index + 1} · 相似度 {result.similarity.toFixed(2)}</p></li>)}</ol>}
  </section>;
}
