import { AppShell } from "@/components/app-shell";
import { AuthenticatedApp } from "@/components/app/authenticated-app";

export default function AppPage() {
  return <AppShell><AuthenticatedApp /></AppShell>;
}
