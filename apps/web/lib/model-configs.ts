import { apiRequest } from "./api-client";

export interface DeepSeekConfig {
  is_configured: boolean;
  api_key_hint: string | null;
  default_model: string;
}

export function getDeepSeekConfig(): Promise<DeepSeekConfig | undefined> {
  return apiRequest<DeepSeekConfig>("/model-configs/deepseek");
}

export function saveDeepSeekConfig(apiKey: string): Promise<DeepSeekConfig | undefined> {
  return apiRequest<DeepSeekConfig>("/model-configs/deepseek", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey }),
  });
}
