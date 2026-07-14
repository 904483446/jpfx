"use client";

import { type FormEvent, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/auth";
import { ApiClientError } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type AuthFormProps = { mode: "login" | "register" };
type FormValues = { displayName: string; email: string; password: string };
const initialValues: FormValues = { displayName: "", email: "", password: "" };

function validate(values: FormValues, mode: AuthFormProps["mode"]): string | null {
  if (mode === "register" && !values.displayName.trim()) return "请填写昵称";
  if (!values.email.trim()) return "请填写邮箱地址";
  if (!/^\S+@\S+\.\S+$/.test(values.email)) return "请输入有效的邮箱地址";
  if (!values.password) return "请填写密码";
  if (values.password.length < 8 || values.password.length > 128) return "密码长度应为 8 到 128 个字符";
  return null;
}

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const [values, setValues] = useState(initialValues);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const submissionLock = useRef(false);
  const isRegister = mode === "register";
  const errorId = "auth-form-error";
  const updateValue = (field: keyof FormValues, value: string) => setValues((current) => ({ ...current, [field]: value }));

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isSubmitting || submissionLock.current) return;
    const validationMessage = validate(values, mode);
    if (validationMessage) { setError(validationMessage); return; }
    setError(null);
    submissionLock.current = true;
    setIsSubmitting(true);
    try {
      if (isRegister) {
        await register({ displayName: values.displayName.trim(), email: values.email.trim(), password: values.password });
        router.replace("/login");
      } else {
        await login({ email: values.email.trim(), password: values.password });
        router.replace("/app");
      }
    } catch (caughtError) {
      setError(caughtError instanceof ApiClientError ? caughtError.message : "网络请求失败，请稍后重试");
    } finally {
      submissionLock.current = false;
      setIsSubmitting(false);
    }
  };

  return <form className="space-y-4" noValidate onSubmit={onSubmit}>
    {isRegister && <div className="space-y-2"><label className="text-sm font-medium text-slate-700" htmlFor="display-name">昵称</label><Input aria-describedby={error ? errorId : undefined} disabled={isSubmitting} id="display-name" onChange={(event) => updateValue("displayName", event.target.value)} value={values.displayName} /></div>}
    <div className="space-y-2"><label className="text-sm font-medium text-slate-700" htmlFor="email">邮箱地址</label><Input aria-describedby={error ? errorId : undefined} autoComplete="email" disabled={isSubmitting} id="email" onChange={(event) => updateValue("email", event.target.value)} type="email" value={values.email} /></div>
    <div className="space-y-2"><label className="text-sm font-medium text-slate-700" htmlFor="password">密码</label><Input aria-describedby={error ? errorId : undefined} autoComplete={isRegister ? "new-password" : "current-password"} disabled={isSubmitting} id="password" onChange={(event) => updateValue("password", event.target.value)} type="password" value={values.password} /></div>
    {error && <p className="text-sm text-red-600" id={errorId} role="alert">{error}</p>}
    <Button className="mt-2 h-10 w-full bg-[#1677ff] hover:bg-[#146be6]" disabled={isSubmitting} type="submit">{isSubmitting ? "提交中…" : isRegister ? "注册" : "登录"}</Button>
  </form>;
}
