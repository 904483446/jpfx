import { apiRequest } from "./api-client";

export interface CandidateEvidence { source_title: string; source_url: string | null; excerpt: string | null; }
export interface AnalysisCandidate { id: string; name: string; description: string | null; source_type: string; is_selected: boolean; sort_order: number | null; evidence: CandidateEvidence[]; }
export interface AnalysisAgentRun { attempt: number; agent_key: "evidence_collection" | "quality_check" | "model_analysis" | "report_generation"; status: "queued" | "running" | "completed" | "failed" | "skipped"; started_at: string | null; completed_at: string | null; failure_reason: string | null; }
export interface AnalysisTask { id: string; space_id: string; title: string; industry: string; product_direction: string; keywords: string[]; known_competitors: string[]; discovery_mode: string; status: "draft" | "queued" | "running" | "completed" | "failed"; stage: string | null; completed_at: string | null; final_competitors: string[]; candidates: AnalysisCandidate[]; agent_runs: AnalysisAgentRun[]; }
export interface CreateAnalysisTaskInput { title: string; industry: string; productDirection: string; keywords: string[]; knownCompetitors: string[]; discoveryMode: "manual" | "semi_auto" | "auto"; }

export function createAnalysisTask(spaceId: string, input: CreateAnalysisTaskInput) {
  return apiRequest<AnalysisTask>(`/spaces/${spaceId}/analysis-tasks`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: input.title.trim(), industry: input.industry.trim(), product_direction: input.productDirection.trim(), keywords: input.keywords.map((item) => item.trim()).filter(Boolean), known_competitors: input.knownCompetitors.map((item) => item.trim()).filter(Boolean), discovery_mode: input.discoveryMode }) });
}
export function getAnalysisTask(taskId: string) { return apiRequest<AnalysisTask>(`/analysis-tasks/${taskId}`); }
export function discoverCandidates(taskId: string) { return apiRequest<AnalysisTask>(`/analysis-tasks/${taskId}/candidates/discover`, { method: "POST" }); }
export function selectCompetitors(taskId: string, candidateIds: string[]) { return apiRequest<AnalysisTask>(`/analysis-tasks/${taskId}/competitors`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ candidate_ids: candidateIds }) }); }
export function autoSelectCompetitors(taskId: string) { return apiRequest<AnalysisTask>(`/analysis-tasks/${taskId}/competitors/auto-select`, { method: "POST" }); }
export function runAnalysisTask(taskId: string) { return apiRequest<AnalysisTask>(`/analysis-tasks/${taskId}/run`, { method: "POST" }); }
export function retryAnalysisTask(taskId: string) { return apiRequest<AnalysisTask>(`/analysis-tasks/${taskId}/retry`, { method: "POST" }); }
