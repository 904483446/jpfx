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

  return <section className="mt-10 max-w-3xl" aria-labelledby="space-retrieval-heading">
    <p className="text-sm font-medium text-[#14b8a6]">知识库</p>
    <h2 className="mt-2 text-2xl font-semibold tracking-tight" id="space-retrieval-heading">空间检索</h2>
    <p className="mt-2 text-sm text-slate-500">检索当前空间中已索引文档的相关片段。</p>
    <div className="mt-4 flex flex-wrap gap-3 rounded-2xl border border-slate-200 bg-white p-5">
      <label className="sr-only" htmlFor="retrieval-query">检索问题</label>
      <input aria-label="检索问题" className="min-w-56 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm" disabled={isSearching} id="retrieval-query" onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void onSearch(); }} placeholder="例如：目标用户是谁？" value={query} />
      <Button disabled={!query.trim() || isSearching} onClick={() => void onSearch()} type="button">{isSearching ? "检索中…" : "检索"}</Button>
    </div>
    {error && <p className="mt-4 text-sm text-red-600" role="alert">{error}</p>}
    {results?.length === 0 && <p className="mt-4 rounded-2xl border border-dashed border-slate-300 bg-white p-5 text-sm text-slate-600">没有找到相关文档片段</p>}
    {results && results.length > 0 && <ol className="mt-4 space-y-3">{results.map((result) => <li className="rounded-2xl border border-slate-200 bg-white p-4" key={`${result.filename}-${result.chunk_index}-${result.content}`}><p className="whitespace-pre-wrap text-sm leading-6">{result.content}</p><p className="mt-3 text-xs text-slate-500">{result.filename} · 片段 {result.chunk_index + 1} · 相似度 {result.similarity.toFixed(2)}</p></li>)}</ol>}
  </section>;
}
