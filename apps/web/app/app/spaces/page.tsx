import { AuthenticatedApp } from "@/components/app/authenticated-app";
import { AppShell } from "@/components/app-shell";

export default function SpacesPage() {
  return <AppShell><AuthenticatedApp /></AppShell>;
}
