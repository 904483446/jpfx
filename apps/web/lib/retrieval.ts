import { apiRequest } from "./api-client";
import type { DocumentRecord } from "./documents";

export interface RetrievalResult {
  content: string;
  filename: string;
  chunk_index: number;
  similarity: number;
}

export interface RetrievalResponse {
  results: RetrievalResult[];
}

export function indexDocument(documentId: string): Promise<DocumentRecord | undefined> {
  return apiRequest<DocumentRecord>(`/documents/${documentId}/index`, { method: "POST" });
}

export function searchSpaceDocuments(
  spaceId: string,
  query: string,
  topK = 8,
): Promise<RetrievalResponse | undefined> {
  return apiRequest<RetrievalResponse>(`/spaces/${spaceId}/retrieval/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
}
