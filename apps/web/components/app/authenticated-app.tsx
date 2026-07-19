"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardSpaces } from "@/components/app/dashboard-spaces";
import { Button } from "@/components/ui/button";
import { getCurrentUser, type CurrentUser } from "@/lib/auth";
import { ApiClientError } from "@/lib/api-client";

export function AuthenticatedApp() {
  const { replace } = useRouter();
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [error, setError] = useState<string | null>(null);
  const requestVersion = useRef(0);

  const loadCurrentUser = useCallback(async () => {
    const currentRequestVersion = ++requestVersion.current;
    try {
      const currentUser = await getCurrentUser();
      if (currentRequestVersion !== requestVersion.current) return;
      if (!currentUser) { setError("网络请求失败，请稍后重试"); setStatus("error"); return; }
      setUser(currentUser); setStatus("ready");
    } catch (caughtError) {
      if (currentRequestVersion !== requestVersion.current) return;
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") { replace("/login"); return; }
      setError(caughtError instanceof ApiClientError ? caughtError.message : "网络请求失败，请稍后重试"); setStatus("error");
    }
  }, [replace]);

  useEffect(() => { let active = true; void Promise.resolve().then(() => { if (active) return loadCurrentUser(); }); return () => { active = false; requestVersion.current += 1; }; }, [loadCurrentUser]);
  const retry = () => { setStatus("loading"); setError(null); void loadCurrentUser(); };

  if (status === "loading") return <div aria-busy="true" className="max-w-5xl space-y-6" data-testid="auth-loading-skeleton"><div className="h-3 w-20 animate-pulse bg-muted" /><div className="h-9 w-64 max-w-full animate-pulse bg-muted" /><div className="grid gap-4 md:grid-cols-2"><div className="h-40 animate-pulse border border-border bg-card" /><div className="h-40 animate-pulse border border-border bg-card" /></div><span className="sr-only">正在验证登录状态…</span></div>;
  if (status === "error") return <div className="space-y-4"><p className="text-sm text-destructive" role="alert">{error}</p><Button onClick={retry} type="button">重试</Button></div>;
  return <DashboardSpaces user={user!} />;
}
