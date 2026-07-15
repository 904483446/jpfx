import { apiRequest } from "./api-client";

export interface Space {
  id: string;
  name: string;
  industry: string | null;
  product_direction: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateSpaceInput {
  name: string;
  industry: string;
  productDirection: string;
  description: string;
}

function optionalText(value: string): string | undefined {
  return value.trim() || undefined;
}

export async function listSpaces(): Promise<Space[]> {
  return (await apiRequest<Space[]>("/spaces")) ?? [];
}

export function createSpace(input: CreateSpaceInput): Promise<Space | undefined> {
  const industry = optionalText(input.industry);
  const productDirection = optionalText(input.productDirection);
  const description = optionalText(input.description);

  return apiRequest<Space>("/spaces", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: input.name.trim(),
      ...(industry ? { industry } : {}),
      ...(productDirection ? { product_direction: productDirection } : {}),
      ...(description ? { description } : {}),
    }),
  });
}
