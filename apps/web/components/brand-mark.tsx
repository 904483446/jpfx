import Link from "next/link";

export function BrandMark() {
  return (
    <Link className="inline-flex items-center gap-3 font-semibold tracking-tight text-foreground" href="/">
      <span aria-hidden="true" className="grid size-7 place-items-center border border-current text-xs font-mono">
        档
      </span>
      <span>竞品智研台</span>
    </Link>
  );
}
