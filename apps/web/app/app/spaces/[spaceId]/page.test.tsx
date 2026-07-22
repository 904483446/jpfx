import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("next/navigation", () => ({ useParams: () => ({ spaceId: "space-1" }) }));
vi.mock("@/components/app-shell", () => ({ AppShell: ({ children }: { children: React.ReactNode }) => <main>{children}</main> }));
vi.mock("@/components/app/space-documents", () => ({ SpaceDocuments: () => <div /> }));
vi.mock("@/components/app/space-retrieval", () => ({ SpaceRetrieval: () => <div /> }));

import SpaceDocumentsPage from "./page";

describe("SpaceDocumentsPage", () => {
  it("uses paper semantic tokens for its header and primary token for the analysis CTA", () => {
    render(<SpaceDocumentsPage />);

    const header = screen.getByRole("heading", { level: 1 }).parentElement!;
    const cta = screen.getByRole("link", { name: "新建分析任务" });

    expect(header).toHaveClass("border-border", "bg-card", "text-card-foreground");
    expect(header.className).not.toMatch(/(?:^|\s)(?:bg|text|border)-(?:slate|cyan)-/);
    expect(header).not.toHaveClass("shadow-sm");
    expect(cta).toHaveClass("bg-primary", "text-primary-foreground");
    expect(cta.className).not.toMatch(/(?:^|\s)(?:bg|text)-cyan-/);
  });
});
