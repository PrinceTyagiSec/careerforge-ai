// API Client for CareerForge AI
const BASE_URL = '/api';

export interface CandidateProfile {
  id: number;
  user_id: number;
  headline?: string;
  summary?: string;
  location: string;
  remote_preference: string;
  target_role?: string;
  years_of_experience: number;
  expected_salary_min?: number;
  expected_salary_max?: number;
  currency: string;
  availability?: string;
  work_authorization?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  phone?: string;
}

export interface ProviderCredential {
  provider_name: string;
  app_id_or_user?: string;
  is_enabled: boolean;
  has_key: boolean;
  masked_key: string;
}

export interface JobItem {
  id: number;
  title: string;
  company_name: string;
  location: string;
  city?: string;
  remote_status: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  freshness_status: string;
  is_url_valid: boolean;
  canonical_url: string;
  match_score?: number;
  matching_skills: string[];
  missing_skills: string[];
  is_saved: boolean;
  application_status?: string;
  sources: { provider_name: string; source_url: string }[];
  published_at?: string;
  discovered_at?: string;
}

export interface JobDetail extends JobItem {
  description: string;
  requirements: { id: number; category: string; text: string; canonical: string }[];
  match: {
    overall_score: number;
    deterministic_score: number;
    skill_score: number;
    experience_score: number;
    location_score: number;
    salary_score: number;
    matching_skills: string[];
    partial_skills: string[];
    missing_skills: string[];
    transferable_skills: string[];
    explanation_summary: string;
    gap_analysis: any;
  };
  evidence: {
    id: number;
    requirement_term: string;
    match_status: string;
    candidate_claim?: string;
    source_reference?: string;
    confidence: number;
    verification_status: string;
  }[];
  application_id?: number;
}

export interface ResumeDetail {
  id: number;
  original_filename: string;
  file_type: string;
  raw_text?: string;
  ocr_applied: boolean;
  ocr_confidence?: number;
  parsing_status: string;
  skills: { id: number; name: string; canonical_name: string; category: string; proficiency: string }[];
  experiences: { id: number; company: string; title: string; location: string; start_date: string; end_date: string; bullets: string[] }[];
  educations: { id: number; institution: string; degree: string; field_of_study: string }[];
  projects: { id: number; title: string; description: string; bullets: string[] }[];
  claims: { id: number; category: string; statement: string; source_section?: string; verification_status: string; confidence: number }[];
}

export interface ResumeQuality {
  overall_quality_score: number;
  category_scores: { content: number; readability: number; ats: number; completeness: number };
  metrics: { total_skills: number; total_experiences: number; total_bullets: number; measurable_outcomes_count: number; word_count: number };
  issues: {
    content: { severity: string; message: string }[];
    readability: { severity: string; message: string }[];
    ats: { severity: string; message: string }[];
    completeness: { severity: string; message: string }[];
  };
}

export interface ApplicationItem {
  id: number;
  job_id: number;
  job_title: string;
  company_name: string;
  location: string;
  status: string;
  applied_at: string;
  follow_up_date?: string;
  interview_date?: string;
  deadline_date?: string;
  salary_offered?: number;
  outcome?: string;
  events_count: number;
  notes_count: number;
}

export interface SavedSearchItem {
  id: number;
  name: string;
  keywords?: string;
  location: string;
  remote_preference: string;
  min_salary?: number;
  is_enabled: boolean;
  frequency_minutes: number;
  last_run_at?: string;
  next_run_at?: string;
  total_found_count: number;
  high_match_count: number;
  notify_telegram: boolean;
  min_match_threshold: number;
}

export interface DashboardAnalytics {
  total_jobs_discovered: number;
  total_jobs_saved: number;
  total_applied: number;
  total_interviews: number;
  total_offers: number;
  response_rate_pct: number;
  applications_by_status: Record<string, number>;
  top_skill_gaps: { skill: string; count: number }[];
  resume_quality_score?: number;
  telegram_connected: boolean;
  ollama_status: string;
  provider_health: { provider_name: string; status: string; last_checked_at?: string; error_message?: string }[];
}

// Helper fetch wrapper
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Profile
  getProfile: () => apiFetch<CandidateProfile>('/profile'),
  updateProfile: (data: Partial<CandidateProfile>) => apiFetch<CandidateProfile>('/profile', { method: 'PUT', body: JSON.stringify(data) }),
  getPreferences: () => apiFetch<any>('/profile/preferences'),
  updatePreferences: (data: any) => apiFetch<any>('/profile/preferences', { method: 'PUT', body: JSON.stringify(data) }),

  // Resumes
  listResumes: () => apiFetch<any[]>('/resumes'),
  getResumeDetail: (id: number) => apiFetch<ResumeDetail>(`/resumes/${id}`),
  getResumeQuality: (id: number) => apiFetch<ResumeQuality>(`/resumes/${id}/quality`),
  reparseResume: (id: number) => apiFetch<any>(`/resumes/${id}/reparse`, { method: 'POST' }),
  uploadResume: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${BASE_URL}/resumes/upload`, { method: 'POST', body: formData });
    if (!res.ok) throw new Error('Failed to upload resume');
    return res.json();
  },

  // Jobs
  listJobs: (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return apiFetch<{ total: number; page: number; results: JobItem[] }>(`/jobs?${query}`);
  },
searchLiveJobs: (params?: {
  keywords?: string;
  location?: string;
  remote_status?: string;
  min_salary?: number;
}) => {
  const query = new URLSearchParams();

  if (params?.keywords) {
    query.append('keywords', params.keywords);
  }

  if (params?.location) {
    query.append('location', params.location);
  }

  if (params?.remote_status) {
    query.append('remote_status', params.remote_status);
  }

  if (params?.min_salary !== undefined) {
    query.append('min_salary', String(params.min_salary));
  }

  return apiFetch<{ count: number; results: JobItem[] }>(
    `/jobs/search-live?${query.toString()}`,
    { method: 'POST' }
  );
},
  importJob: (data: any) => apiFetch<any>('/jobs/import', { method: 'POST', body: JSON.stringify(data) }),
  getJobDetail: (id: number) => apiFetch<JobDetail>(`/jobs/${id}`),
  toggleSaveJob: (id: number) => apiFetch<any>(`/jobs/${id}/toggle-save`, { method: 'POST' }),
  tailorResume: (id: number, template: string = 'ATS Simple') => apiFetch<any>(`/jobs/${id}/tailor?template=${encodeURIComponent(template)}`, { method: 'POST' }),
  reviewChange: (jobId: number, changeId: number, action: { status: string; user_override_text?: string }) =>
    apiFetch<any>(`/jobs/${jobId}/tailor/changes/${changeId}`, { method: 'PUT', body: JSON.stringify(action) }),
  getCoverLetter: (jobId: number) => apiFetch<any>(`/jobs/${jobId}/cover-letter`),
  updateCoverLetter: (jobId: number, content: string) => apiFetch<any>(`/jobs/${jobId}/cover-letter`, { method: 'PUT', body: JSON.stringify({ content }) }),

  // Applications
  listApplications: () => apiFetch<ApplicationItem[]>('/applications'),
  getApplicationDetail: (id: number) => apiFetch<any>(`/applications/${id}`),
  createApplication: (data: any) => apiFetch<any>('/applications', { method: 'POST', body: JSON.stringify(data) }),
  updateApplicationStatus: (id: number, data: any) => apiFetch<any>(`/applications/${id}/status`, { method: 'PUT', body: JSON.stringify(data) }),
  addApplicationNote: (id: number, content: string) => apiFetch<any>(`/applications/${id}/notes?content=${encodeURIComponent(content)}`, { method: 'POST' }),

  // Saved Searches
  listSavedSearches: () => apiFetch<SavedSearchItem[]>('/saved-searches'),
  createSavedSearch: (data: any) => apiFetch<SavedSearchItem>('/saved-searches', { method: 'POST', body: JSON.stringify(data) }),
  runSavedSearchNow: (id: number) => apiFetch<any>(`/saved-searches/${id}/run-now`, { method: 'POST' }),
  deleteSavedSearch: (id: number) => apiFetch<any>(`/saved-searches/${id}`, { method: 'DELETE' }),

  // Companies
  listCompanies: () => apiFetch<any[]>('/companies'),
  getCompanyDetail: (id: number) => apiFetch<any>(`/companies/${id}`),

  // Telegram
  getTelegramStatus: () => apiFetch<any>('/telegram'),
  configureTelegram: (bot_token: string, chat_id: string, is_enabled: boolean = true) =>
    apiFetch<any>('/telegram/configure', { method: 'POST', body: JSON.stringify({ bot_token, chat_id, is_enabled }) }),
  testTelegram: () => apiFetch<any>('/telegram/test', { method: 'POST' }),
  updateTelegramPrefs: (data: any) => apiFetch<any>('/telegram/preferences', { method: 'PUT', body: JSON.stringify(data) }),
  getTelegramHistory: () => apiFetch<any[]>('/telegram/history'),

  // Providers & Analytics
  getProvidersHealth: () => apiFetch<any>('/providers/health'),
  getCredentials: () => apiFetch<ProviderCredential[]>('/providers/credentials'),
  updateCredentials: (data: any) => apiFetch<any>('/providers/credentials', { method: 'POST', body: JSON.stringify(data) }),
  getDashboardAnalytics: () => apiFetch<DashboardAnalytics>('/analytics/dashboard'),
  listBackgroundTasks: () => apiFetch<any[]>('/analytics/tasks'),
};
