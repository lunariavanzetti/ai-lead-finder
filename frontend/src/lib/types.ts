export type JobStatus = 'pending' | 'running' | 'paused' | 'cancelled' | 'completed' | 'failed'

export interface RequiredInformation {
  business_name: boolean
  website: boolean
  phone: boolean
  email: boolean
  address: boolean
  google_rating: boolean
  google_reviews_count: boolean
  opening_hours: boolean
  facebook: boolean
  instagram: boolean
  linkedin_company_page: boolean
  booking_link: boolean
  contact_form: boolean
  staff_page: boolean
  about_page: boolean
  decision_maker_linkedin: boolean
}

export interface AdvancedSettings {
  concurrent_workers: number
  timeout_seconds: number
  retries: number
  delay_seconds: number
  export_folder: string | null
  proxy_url: string | null
  rotate_user_agent: boolean
  capture_screenshots: boolean
}

export interface SearchRequest {
  business_type: string
  country: string
  state: string | null
  city: string
  radius_km: number
  max_results: number
  decision_maker_titles: string[]
  required_information: RequiredInformation
  advanced_settings: AdvancedSettings
}

export interface JobCreatedResponse {
  job_id: string
  status: JobStatus
}

export interface JobSummary {
  id: string
  status: JobStatus
  params: SearchRequest
  businesses_found: number
  businesses_analyzed: number
  emails_found: number
  websites_scanned: number
  created_at: string
  started_at: string | null
  finished_at: string | null
}

export interface ProgressEvent {
  type: 'status' | 'discovery_complete' | 'progress'
  status?: JobStatus
  message?: string
  businesses_found?: number
  businesses_analyzed?: number
  emails_found?: number
  websites_scanned?: number
  estimated_remaining_seconds?: number
  current_business?: string
  current_step?: string
  lead_score?: number
}

export interface StaffMember {
  id: string
  full_name: string
  title: string | null
  email: string | null
  linkedin_url: string | null
  is_decision_maker: boolean
  priority_rank: number
}

export interface PainPoint {
  code: string
  label: string
  severity: 'high' | 'medium' | 'low'
}

export interface LeadListItem {
  id: string
  lead_score: number
  business_name: string
  business_type: string
  website: string | null
  phone: string | null
  email: string | null
  city: string | null
  state: string | null
  country: string | null
  google_rating: number | null
  google_reviews_count: number | null
  status: string
  owner_name: string | null
  owner_title: string | null
  pain_points: PainPoint[]
  recommended_services: string[]
}

export interface LeadDetail extends LeadListItem {
  address: string | null
  google_maps_url: string | null
  opening_hours: Record<string, unknown> | null
  facebook_url: string | null
  instagram_url: string | null
  linkedin_company_url: string | null
  whatsapp_detected: boolean
  messenger_detected: boolean
  booking_link: string | null
  has_contact_form: boolean
  has_staff_page: boolean
  has_about_page: boolean
  technologies: Record<string, boolean | number | null>
  pain_points: PainPoint[]
  recommended_services: string[]
  score_breakdown: {
    pain_point_component: number
    contactability_component: number
    decision_maker_component: number
    max_pain_point_component: number
    total: number
  }
  estimated_hours_saved_per_week: number | null
  strengths: string[]
  outreach_message: string | null
  follow_up_message: string | null
  discovery_questions: string[]
  screenshot_path: string | null
  crawl_error: string | null
  staff: StaffMember[]
  created_at: string
  updated_at: string
}

export interface LeadListResponse {
  items: LeadListItem[]
  total: number
  page: number
  page_size: number
}

export interface DashboardStats {
  total_leads: number
  total_jobs: number
  average_lead_score: number
  high_priority_leads: number
  top_pain_points: { label: string; count: number }[]
  recent_jobs: {
    id: string
    status: JobStatus
    business_type: string | null
    city: string | null
    businesses_analyzed: number
    created_at: string | null
  }[]
}

export interface AppSettings {
  theme: 'dark' | 'light' | 'system'
  export_folder: string | null
  language: string
  auto_save: boolean
}

export interface SearchHistoryItem {
  id: string
  job_id: string
  business_type: string
  location_label: string
  params: SearchRequest
  result_count: number
}

export type ExportFormat = 'csv' | 'xlsx' | 'json' | 'sqlite'
