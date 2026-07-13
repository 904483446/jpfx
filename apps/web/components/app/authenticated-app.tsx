"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, type CurrentUser } from "@/lib/auth";
import { ApiClientError } from "@/lib/api-client";
import { Button } from "@/components/ui/button";

export function AuthenticatedApp() {
  const { replace } = useRouter();
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadCurrentUser = useCallback(async () => {
    try {
      const currentUser = await getCurrentUser();

      if (!currentUser) {
        replace("/login");
        return;
      }

      setUser(currentUser);
      setStatus("ready");
    } catch (caughtError) {
      if (caughtError instanceof ApiClientError && caughtError.code === "UNAUTHORIZED") {
        replace("/login");
        return;
      }

      setError(caughtError instanceof ApiClientError ? caughtError.message : "网络请求失败，请稍后重试");
      setStatus("error");
    }
  }, [replace]);

  useEffect(() => {
    void Promise.resolve().then(loadCurrentUser);
  }, [loadCurrentUser]);

  const retry = () => {
    setStatus("loading");
    setError(null);
    void loadCurrentUser();
  };

  if (status === "loading") {
    return <p className="text-sm text-slate-500">正在验证登录状态…</p>;
  }

  if (status === "error") {
    return <div className="space-y-4"><p className="text-sm text-red-600" role="alert">{error}</p><Button onClick={retry} type="button">重试</Button></div>;
  }

  return <div className="max-w-3xl"><p className="text-sm font-medium text-[#14b8a6]">工作台</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">欢迎回来，{user!.display_name}</h1><p className="mt-2 text-sm text-slate-500">{user!.email}</p><div className="mt-8 rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">Task 9 将在这里展示你的空间列表。</div></div>;
}
