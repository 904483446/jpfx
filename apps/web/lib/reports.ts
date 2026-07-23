import { ApiClientError, apiRequest, getApiBaseUrl } from "./api-client";

export type EvidenceSourceType = "web" | "private_knowledge" | "model_inference";

export interface ReportCompetitor {
  name: string;
  positioning?: string;
  core_features?: string[];
  target_users?: string[];
  business_model?: string;
  ai_capabilities?: string[];
  strengths?: string[];
  weaknesses?: string[];
  differentiation_opportunities?: string[];
  recommendations?: string[];
  risks?: string[];
}

export interface ReportContent {
  executive_summary?: string;
  competitors?: ReportCompetitor[];
}

export interface CompetitorReport {
  id: string;
  space_id: string;
  task_id: string;
  title: string;
  structured_json: ReportContent;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface ReportEvidence {
  id: string;
  source_type: EvidenceSourceType;
  source_title: string;
  source_url: string | null;
  quote: string | null;
  retrieved_at: string | null;
}

export function getReport(reportId: string) {
  return apiRequest<CompetitorReport>(`/reports/${reportId}`);
}

export function listReports(spaceId?: string) {
  const query = spaceId ? `?space_id=${encodeURIComponent(spaceId)}` : "";
  return apiRequest<CompetitorReport[]>(`/reports${query}`);
}

export function getReportEvidence(reportId: string) {
  return apiRequest<ReportEvidence[]>(`/reports/${reportId}/evidence`);
}

export async function downloadReport(reportId: string, format: "pdf" | "docx"): Promise<void> {
  const response = await fetch(`${getApiBaseUrl()}/reports/${reportId}/export/${format}`, {
    credentials: "include",
  });

  if (!response.ok) {
    const body = await readErrorBody(response);
    throw new ApiClientError(body?.code ?? "NETWORK_ERROR", body?.message ?? "下载报告失败，请稍后重试", body?.details ?? {});
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = fileName(response.headers.get("Content-Disposition"), reportId, format);
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
}

async function readErrorBody(response: Response): Promise<{ code: string; message: string; details: Record<string, unknown> } | null> {
  try {
    const body: unknown = await response.json();
    if (typeof body !== "object" || body === null || !("error" in body)) return null;
    const error = body.error;
    if (typeof error !== "object" || error === null || !("code" in error) || !("message" in error)) return null;
    const details = "details" in error ? error.details : undefined;
    return {
      code: typeof error.code === "string" ? error.code : "NETWORK_ERROR",
      message: typeof error.message === "string" ? error.message : "下载报告失败，请稍后重试",
      details: typeof details === "object" && details !== null && !Array.isArray(details) ? details as Record<string, unknown> : {},
    };
  } catch {
    return null;
  }
}

function fileName(disposition: string | null, reportId: string, format: "pdf" | "docx"): string {
  const match = disposition?.match(/filename="?([^";]+)"?/i);
  return match?.[1] || `competitor-report-${reportId}.${format}`;
}
