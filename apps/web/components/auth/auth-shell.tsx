import type { ReactNode } from "react";
import { BrandMark } from "@/components/brand-mark";

type AuthShellProps = { title: string; description: string; children: ReactNode; footer: ReactNode };

export function AuthShell({ title, description, children, footer }: AuthShellProps) {
  return <main className="grid min-h-screen place-items-center bg-[#f6f9fb] p-6"><section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10"><BrandMark /><h1 className="mt-10 text-3xl font-semibold tracking-tight text-[#0a1f33]">{title}</h1><p className="mt-2 text-sm leading-6 text-slate-500">{description}</p><div className="mt-8">{children}</div><div className="mt-6 text-center text-sm text-slate-500">{footer}</div></section></main>;
}
