import { apiRequest } from "./api-client";

export type DocumentStatus = "uploaded" | "processing" | "indexed" | "failed";

export interface DocumentRecord {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: DocumentStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export async function listDocuments(spaceId: string): Promise<DocumentRecord[]> {
  return (await apiRequest<DocumentRecord[]>(`/spaces/${spaceId}/documents`)) ?? [];
}

export function uploadDocument(
  spaceId: string,
  file: File,
): Promise<DocumentRecord | undefined> {
  const body = new FormData();
  body.append("file", file);
  return apiRequest<DocumentRecord>(`/spaces/${spaceId}/documents`, {
    method: "POST",
    body,
  });
}

export function deleteDocument(documentId: string): Promise<void | undefined> {
  return apiRequest<void>(`/documents/${documentId}`, { method: "DELETE" });
}
