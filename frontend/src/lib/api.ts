import type {
  AppSettings,
  DashboardStats,
  ExportFormat,
  JobCreatedResponse,
  JobSummary,
  LeadDetail,
  LeadListResponse,
  SearchHistoryItem,
  SearchRequest,
} from './types'

// In local dev, Vite proxies "/api" to the backend (see vite.config.ts), so a
// relative path works. In production the frontend and backend are separate
// deployments (e.g. Vercel + Railway), so VITE_API_BASE_URL must point at the
// deployed backend's origin — set it in the frontend's hosting environment.
const BASE_URL = `${import.meta.env.VITE_API_BASE_URL ?? ''}/api`

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  startJob: (payload: SearchRequest) =>
    request<JobCreatedResponse>('/jobs', { method: 'POST', body: JSON.stringify(payload) }),

  listJobs: (limit = 20) => request<JobSummary[]>(`/jobs?limit=${limit}`),

  getJob: (jobId: string) => request<JobSummary>(`/jobs/${jobId}`),

  pauseJob: (jobId: string) => request(`/jobs/${jobId}/pause`, { method: 'POST' }),
  resumeJob: (jobId: string) => request(`/jobs/${jobId}/resume`, { method: 'POST' }),
  cancelJob: (jobId: string) => request(`/jobs/${jobId}/cancel`, { method: 'POST' }),

  listLeads: (params: {
    jobId?: string
    search?: string
    businessType?: string
    city?: string
    status?: string
    minScore?: number
    sortBy?: string
    sortDir?: 'asc' | 'desc'
    page?: number
    pageSize?: number
  }) => {
    const qs = new URLSearchParams()
    if (params.jobId) qs.set('job_id', params.jobId)
    if (params.search) qs.set('search', params.search)
    if (params.businessType) qs.set('business_type', params.businessType)
    if (params.city) qs.set('city', params.city)
    if (params.status) qs.set('status', params.status)
    if (params.minScore !== undefined) qs.set('min_score', String(params.minScore))
    qs.set('sort_by', params.sortBy ?? 'lead_score')
    qs.set('sort_dir', params.sortDir ?? 'desc')
    qs.set('page', String(params.page ?? 1))
    qs.set('page_size', String(params.pageSize ?? 25))
    return request<LeadListResponse>(`/leads?${qs.toString()}`)
  },

  getLead: (leadId: string) => request<LeadDetail>(`/leads/${leadId}`),

  updateLeadStatus: (leadId: string, status: string) =>
    request<LeadDetail>(`/leads/${leadId}`, { method: 'PATCH', body: JSON.stringify({ status }) }),

  getDashboardStats: () => request<DashboardStats>('/dashboard'),

  getSearchHistory: () => request<SearchHistoryItem[]>('/search-history'),

  getSettings: () => request<AppSettings>('/settings'),
  updateSettings: (settings: AppSettings) =>
    request<AppSettings>('/settings', { method: 'PUT', body: JSON.stringify(settings) }),

  async exportLeads(format: ExportFormat, opts: { jobId?: string; leadIds?: string[] }) {
    const res = await fetch(`${BASE_URL}/exports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ format, job_id: opts.jobId, lead_ids: opts.leadIds }),
    })
    if (!res.ok) throw new Error(`Export failed: ${res.status}`)
    const blob = await res.blob()
    const disposition = res.headers.get('Content-Disposition') ?? ''
    const match = disposition.match(/filename="?([^"]+)"?/)
    downloadBlob(blob, match?.[1] ?? `leads_export.${format}`)
  },

  async exportAudit(leadId: string, businessName: string) {
    const res = await fetch(`${BASE_URL}/exports/audit/${leadId}`, { method: 'POST' })
    if (!res.ok) throw new Error(`Audit export failed: ${res.status}`)
    const blob = await res.blob()
    downloadBlob(blob, `audit_${businessName.replace(/\s+/g, '_')}.pdf`)
  },

  jobStreamUrl: (jobId: string) => `${BASE_URL}/jobs/${jobId}/stream`,
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
