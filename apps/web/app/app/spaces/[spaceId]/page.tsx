"use client";

import { useParams } from "next/navigation";

import { SpaceDocuments } from "@/components/app/space-documents";
import { AppShell } from "@/components/app-shell";

export default function SpaceDocumentsPage() {
  const { spaceId } = useParams<{ spaceId: string }>();

  return <AppShell><SpaceDocuments spaceId={spaceId} /></AppShell>;
}
