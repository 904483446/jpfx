import { access } from "node:fs/promises";

for (const routeFile of [
  "app/page.tsx",
  "app/login/page.tsx",
  "app/register/page.tsx",
  "app/app/page.tsx",
  "app/app/spaces/[spaceId]/page.tsx",
]) {
  await access(new URL(`../${routeFile}`, import.meta.url));
}

console.log("STATIC_ROUTE_FILES=ok");
