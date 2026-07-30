import { afterEach, describe, expect, it, vi } from "vitest";

const { apiRequest } = vi.hoisted(() => ({ apiRequest: vi.fn() }));
vi.mock("./api-client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./api-client")>()),
  apiRequest,
}));

import { downloadReport, getReport, getReportEvidence, listReports } from "./reports";

describe("report API client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.clearAllMocks();
    vi.unstubAllEnvs();
  });

  it("loads the structured report and its evidence separately", async () => {
    apiRequest.mockResolvedValueOnce({ id: "report-1" }).mockResolvedValueOnce([]);

    await expect(getReport("report-1")).resolves.toEqual({ id: "report-1" });
    await expect(getReportEvidence("report-1")).resolves.toEqual([]);

    expect(apiRequest).toHaveBeenNthCalledWith(1, "/reports/report-1");
    expect(apiRequest).toHaveBeenNthCalledWith(2, "/reports/report-1/evidence");
  });

  it("loads reports with an optional encoded space filter", async () => {
    apiRequest.mockResolvedValue([]);

    await expect(listReports()).resolves.toEqual([]);
    await expect(listReports("space id")).resolves.toEqual([]);

    expect(apiRequest).toHaveBeenNthCalledWith(1, "/reports");
    expect(apiRequest).toHaveBeenNthCalledWith(2, "/reports?space_id=space%20id");
  });

  it("downloads a PDF using credentialed fetch and the response blob", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://127.0.0.1:8000/api/v1");
    const blob = new Blob(["pdf"], { type: "application/pdf" });
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      blob: vi.fn().mockResolvedValue(blob),
      headers: new Headers({ "Content-Disposition": 'attachment; filename="report.pdf"' }),
    } as unknown as Response);
    const createObjectURL = vi.fn(() => "blob:report");
    const revokeObjectURL = vi.fn();
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);

    await downloadReport("report-1", "pdf");

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/api/v1/reports/report-1/export/pdf", { credentials: "include" });
    expect(createObjectURL).toHaveBeenCalledWith(blob);
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:report");
  });
});
