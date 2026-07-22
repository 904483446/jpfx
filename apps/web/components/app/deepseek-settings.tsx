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

  const configured = config?.is_configured ?? false;

  return (
    <section aria-labelledby="deepseek-settings-heading" className="max-w-5xl">
      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-[0_18px_45px_rgb(49_42_32_/_0.08)] dark:shadow-none">
        <header className="border-b border-border bg-muted/65 px-6 py-6 sm:px-8">
          <p className="text-xs font-semibold tracking-[0.24em] text-primary">MODEL DOSSIER · DEEPSEEK</p>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h1 className="font-heading text-2xl font-semibold tracking-tight text-foreground" id="deepseek-settings-heading">模型访问凭据</h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">密钥仅用于本次提交。页面不回显、不写入浏览器本地存储，只展示服务端返回的脱敏状态。</p>
            </div>
            <span className={`inline-flex w-fit items-center rounded-md border px-2.5 py-1 text-xs font-semibold ${configured ? "border-primary/25 bg-primary/10 text-primary" : "border-border bg-card text-muted-foreground"}`}>
              {configured ? "已配置" : "待配置"}
            </span>
          </div>
        </header>

        <div className="grid gap-px border-b border-border bg-border lg:grid-cols-[minmax(0,1fr)_18rem]">
          <section aria-label="当前配置摘要" className="bg-card p-6 sm:p-8">
            <p className="text-xs font-semibold tracking-[0.18em] text-muted-foreground">CONFIGURATION RECORD</p>
            {isLoading ? (
              <p className="mt-5 text-sm text-muted-foreground">正在读取服务端配置摘要…</p>
            ) : (
              <dl className="mt-5 divide-y divide-border border-y border-border text-sm">
                <div className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
                  <dt className="text-muted-foreground">连接状态</dt>
                  <dd className="font-medium text-foreground">{configured ? "服务端已配置" : "尚未配置"}</dd>
                </div>
                <div className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
                  <dt className="text-muted-foreground">默认模型</dt>
                  <dd className="font-mono text-foreground">{config?.default_model ?? "—"}</dd>
                </div>
                <div className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
                  <dt className="text-muted-foreground">密钥掩码</dt>
                  <dd className="font-mono text-foreground">{config?.api_key_hint ?? "未设置"}</dd>
                </div>
              </dl>
            )}
          </section>

          <aside className="bg-muted/40 p-6 sm:p-8">
            <p className="text-xs font-semibold tracking-[0.18em] text-primary">SECURITY NOTE</p>
            <h2 className="mt-3 text-base font-semibold text-foreground">凭据不留在工作台</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">提交成功后输入框会立即清空；后续页面只使用服务端保管的配置与掩码信息。</p>
          </aside>
        </div>

        <form className="p-6 sm:p-8" onSubmit={(event) => { event.preventDefault(); void saveConfig(); }}>
          <div className="max-w-2xl">
            <label className="block text-sm font-semibold text-foreground" htmlFor="deepseek-api-key">DeepSeek API Key</label>
            <p className="mt-1 text-sm leading-6 text-muted-foreground">输入新的密钥以更新服务端配置。请勿在这里粘贴其他凭据。</p>
            <div className="mt-4 flex flex-col gap-3 sm:flex-row">
              <Input autoComplete="off" className="border-input bg-background text-foreground placeholder:text-muted-foreground focus-visible:border-primary focus-visible:ring-primary/20" disabled={isSaving} id="deepseek-api-key" name="deepseek-api-key" onChange={(event) => setApiKey(event.target.value)} placeholder="输入新的 API Key" type="password" value={apiKey} />
              <Button className="h-9 px-4" disabled={!apiKey.trim() || isSaving} type="submit">{isSaving ? "保存中…" : "保存配置"}</Button>
            </div>
            {error ? <p className="mt-3 text-sm text-destructive" role="alert">{error}</p> : null}
          </div>
        </form>
      </div>
    </section>
  );
}
