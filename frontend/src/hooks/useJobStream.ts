import { useEffect } from 'react'
import { api } from '@/lib/api'
import { useJobStore } from '@/store/jobStore'
import type { ProgressEvent } from '@/lib/types'

/** Subscribes to a job's SSE progress stream and pipes events into the job store. */
export function useJobStream(jobId: string | null) {
  const applyEvent = useJobStore((s) => s.applyEvent)

  useEffect(() => {
    if (!jobId) return

    const source = new EventSource(api.jobStreamUrl(jobId))

    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ProgressEvent
        applyEvent(data)
        if (data.type === 'status' && ['completed', 'cancelled', 'failed'].includes(data.status ?? '')) {
          source.close()
        }
      } catch {
        // ignore malformed frames
      }
    }

    source.onerror = () => {
      source.close()
    }

    return () => source.close()
  }, [jobId, applyEvent])
}
