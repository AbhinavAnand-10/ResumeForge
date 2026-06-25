/**
 * ResumeForge AI — API client
 * Typed wrapper around the FastAPI backend endpoints.
 */

export interface ATSScore {
  overall: number;
  keyword_match: number;
  formatting: number;
  sections_completeness: number;
  readability: number;
}

export interface FlawItem {
  type: string;
  severity: "critical" | "moderate" | "minor";
  location: string;
  description: string;
  suggestion: string;
}

export interface ContentAnalysis {
  strong_points: string[];
  weak_points: string[];
  fluffy_phrases: string[];
  unnecessary_sections: string[];
}

export interface MustHave {
  keyword: string;
  reason: string;
  example_usage: string;
}

export interface DiagnoseResponse {
  session_id: string;
  ats_score: ATSScore;
  flaws: FlawItem[];
  content_analysis: ContentAnalysis;
  must_haves: MustHave[];
  jd_alignment_percent: number | null;
  summary: string;
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  raw_text: string;
  word_count: number;
  char_count: number;
  detected_sections: string[];
}

export interface DiffLine {
  line_no: number;
  original: string;
  optimized: string;
  change_type: "unchanged" | "modified" | "added" | "removed";
  reason: string | null;
}

export interface SkillGapItem {
  skill: string;
  priority: "high" | "medium" | "low";
  suggested_action: string;
  resources: string[];
  estimated_time: string;
}

export interface OptimizeResponse {
  session_id: string;
  original_text: string;
  optimized_text: string;
  diff_lines: DiffLine[];
  projected_ats_score: ATSScore;
  score_delta: number;
  changes_summary: string;
  skill_gap_plan: SkillGapItem[];
  web_sources_used: string[];
}

class APIError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || body.error || detail;
    } catch {
      /* ignore parse failure */
    }
    throw new APIError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export async function uploadResume(
  file: File,
  targetRole: string,
  jobDescription: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_role", targetRole);
  if (jobDescription.trim()) {
    formData.append("job_description", jobDescription);
  }

  const res = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });
  return handleResponse<UploadResponse>(res);
}

export async function diagnoseResume(params: {
  session_id: string;
  raw_text: string;
  target_role: string;
  job_description?: string;
}): Promise<DiagnoseResponse> {
  const res = await fetch("/api/diagnose", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handleResponse<DiagnoseResponse>(res);
}

export async function optimizeResume(params: {
  session_id: string;
  raw_text: string;
  target_role: string;
  job_description?: string;
  diagnosis: DiagnoseResponse;
}): Promise<OptimizeResponse> {
  const res = await fetch("/api/optimize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handleResponse<OptimizeResponse>(res);
}

export async function exportResume(params: {
  session_id: string;
  optimized_text: string;
  target_role: string;
  format: "pdf" | "docx";
}): Promise<Blob> {
  const res = await fetch("/api/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    throw new APIError(res.status, "Export failed");
  }
  return res.blob();
}

export { APIError };
