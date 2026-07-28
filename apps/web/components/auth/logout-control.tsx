"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/auth";

export function LogoutControl() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const isSubmittingRef = useRef(false);

  const handleLogout = async () => {
    if (isSubmittingRef.current) return;

    isSubmittingRef.current = true;
    setIsSubmitting(true);
    setError("");

    try {
      await logout();
      router.replace("/login");
    } catch {
      setError("退出失败，请稍后重试");
    } finally {
      isSubmittingRef.current = false;
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <button
        className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline disabled:cursor-not-allowed disabled:opacity-60"
        disabled={isSubmitting}
        onClick={handleLogout}
        type="button"
      >
        {isSubmitting ? "退出中…" : "退出登录"}
      </button>
      {error ? <p role="alert">{error}</p> : null}
    </div>
  );
}
