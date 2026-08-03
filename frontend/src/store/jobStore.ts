import { create } from 'zustand'
import type { JobStatus, ProgressEvent, SearchRequest } from '@/lib/types'

export interface LogLine {
  id: string
  timestamp: string
  message: string
}

interface JobState {
  activeJobId: string | null
  status: JobStatus | null
  request: SearchRequest | null
  businessesFound: number
  businessesAnalyzed: number
  emailsFound: number
  websitesScanned: number
  estimatedRemainingSeconds: number | null
  currentBusiness: string | null
  currentStep: string | null
  logs: LogLine[]

  startJob: (jobId: string, request: SearchRequest) => void
  applyEvent: (event: ProgressEvent) => void
  reset: () => void
}

const initial = {
  activeJobId: null,
  status: null,
  request: null,
  businessesFound: 0,
  businessesAnalyzed: 0,
  emailsFound: 0,
  websitesScanned: 0,
  estimatedRemainingSeconds: null,
  currentBusiness: null,
  currentStep: null,
  logs: [] as LogLine[],
}

export const useJobStore = create<JobState>((set) => ({
  ...initial,

  startJob: (jobId, request) =>
    set({ ...initial, activeJobId: jobId, request, status: 'pending' }),

  applyEvent: (event) =>
    set((state) => {
      const logs = [...state.logs]
      if (event.type === 'progress' && event.current_business) {
        logs.push({
          id: `${Date.now()}-${Math.random()}`,
          timestamp: new Date().toLocaleTimeString(),
          message: `${event.current_business} — ${event.current_step ?? ''}`.trim(),
        })
      }
      if (event.type === 'status' && event.message) {
        logs.push({
          id: `${Date.now()}-${Math.random()}`,
          timestamp: new Date().toLocaleTimeString(),
          message: event.message,
        })
      }

      return {
        status: event.status ?? state.status,
        businessesFound: event.businesses_found ?? state.businessesFound,
        businessesAnalyzed: event.businesses_analyzed ?? state.businessesAnalyzed,
        emailsFound: event.emails_found ?? state.emailsFound,
        websitesScanned: event.websites_scanned ?? state.websitesScanned,
        estimatedRemainingSeconds: event.estimated_remaining_seconds ?? state.estimatedRemainingSeconds,
        currentBusiness: event.current_business ?? state.currentBusiness,
        currentStep: event.current_step ?? state.currentStep,
        logs: logs.slice(-200),
      }
    }),

  reset: () => set(initial),
}))
