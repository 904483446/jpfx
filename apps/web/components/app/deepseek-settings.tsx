"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/lib/api-client";
import { getDeepSeekConfig, saveDeepSeekConfig, type DeepSeekConfig } from "@/lib/model-configs";

function errorMessage(error: unknown): string {
  return error instanceof ApiClientError ? error.message : "网络请求失败，请稍后重试";
}

export function DeepSeekSettings() {
  const { replace } = useRouter();
  const [config, setConfig] = useState<DeepSeekConfig | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const requestVersion = useRef(0);

  const handleUnauthorized = useCallback((caughtError: unknown): boolean => {
    if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") {
      replace("/login");
      return true;
    }
    return false;
  }, [replace]);

  const loadConfig = useCallback(async () => {
    const request = ++requestVersion.current;
    setIsLoading(true);
    setError(null);
    try {
      const currentConfig = await getDeepSeekConfig();
      if (request === requestVersion.current && currentConfig) setConfig(currentConfig);
    } catch (caughtError) {
      if (request !== requestVersion.current || handleUnauthorized(caughtError)) return;
      setError(errorMessage(caughtError));
    } finally {
      if (request === requestVersion.current) setIsLoading(false);
    }
  }, [handleUnauthorized]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => { if (active) return loadConfig(); });
    return () => { active = false; requestVersion.current += 1; };
  }, [loadConfig]);

  const saveConfig = async () => {
    const keyToSave = apiKey.trim();
    if (!keyToSave || isSaving) return;
    setError(null);
    setIsSaving(true);
    try {
      const updatedConfig = await saveDeepSeekConfig(keyToSave);
      if (updatedConfig) setConfig(updatedConfig);
      setApiKey("");
    } catch (caughtError) {
      if (!handleUnauthorized(caughtError)) setError(errorMessage(caughtError));
    } finally {
      setIsSaving(false);
    }
  };

  return <section aria-labelledby="deepseek-settings-heading" className="max-w-4xl">
    <div className="overflow-hidden rounded-2xl border border-slate-700 bg-[#0a1f33] shadow-2xl shadow-slate-950/20">
      <div className="border-b border-slate-700 bg-[linear-gradient(110deg,#0a1f33,#12304c)] px-6 py-5">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-teal-300">模型控制台 · DeepSeek</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white" id="deepseek-settings-heading">模型访问凭据</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">密钥仅用于本次提交。保存后不会回显、不会保存在浏览器本地，只显示服务端返回的安全状态。</p>
      </div>

      <div className="grid gap-5 p-6 md:grid-cols-[minmax(0,1fr)_13rem]">
        <div className="rounded-xl border border-slate-700 bg-slate-950/45 p-5">
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm font-medium text-slate-100">连接状态</p>
            <span className={config?.is_configured ? "rounded-full bg-teal-400/15 px-2.5 py-1 text-xs font-medium text-teal-200" : "rounded-full bg-amber-400/15 px-2.5 py-1 text-xs font-medium text-amber-200"}>{config?.is_configured ? "已配置" : "待配置"}</span>
          </div>
          {isLoading ? <p className="mt-4 text-sm text-slate-400">正在读取安全配置摘要…</p> : <dl className="mt-4 space-y-3 text-sm"><div className="flex justify-between gap-4 border-t border-slate-800 pt-3"><dt className="text-slate-400">默认模型</dt><dd className="font-mono text-slate-200">{config?.default_model ?? "—"}</dd></div><div className="flex justify-between gap-4"><dt className="text-slate-400">密钥掩码</dt><dd className="font-mono text-slate-200">{config?.api_key_hint ?? "未设置"}</dd></div></dl>}
        </div>

        <div className="rounded-xl border border-teal-400/25 bg-teal-400/5 p-5 text-sm text-teal-50"><p className="font-medium">安全边界</p><p className="mt-2 leading-6 text-teal-100/75">系统不会在页面、Local Storage 或后续响应中保存明文 API Key。</p></div>
      </div>

      <form className="border-t border-slate-700 p-6" onSubmit={(event) => { event.preventDefault(); void saveConfig(); }}>
        <label className="block text-sm font-medium text-slate-100" htmlFor="deepseek-api-key">DeepSeek API Key</label>
        <div className="mt-2 flex flex-col gap-3 sm:flex-row"><Input autoComplete="off" className="border-slate-600 bg-slate-950 text-slate-100 placeholder:text-slate-500" disabled={isSaving} id="deepseek-api-key" name="deepseek-api-key" onChange={(event) => setApiKey(event.target.value)} placeholder="输入新的 API Key 以更新配置" type="password" value={apiKey} /><Button disabled={!apiKey.trim() || isSaving} type="submit">{isSaving ? "保存中…" : "保存配置"}</Button></div>
        <p className="mt-2 text-xs leading-5 text-slate-400">提交成功后输入框会立即清空；请勿在此处粘贴其他凭据。</p>
        {error && <p className="mt-3 text-sm text-red-300" role="alert">{error}</p>}
      </form>
    </div>
  </section>;
}
