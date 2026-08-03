import { useJobStore } from '@/store/jobStore'
import { SearchForm } from '@/components/lead-finder/SearchForm'
import { ProgressPanel } from '@/components/lead-finder/ProgressPanel'

export function LeadFinderPage() {
  const activeJobId = useJobStore((s) => s.activeJobId)
  const reset = useJobStore((s) => s.reset)

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 pb-16">
      {activeJobId ? <ProgressPanel onNewSearch={reset} /> : <SearchForm />}
    </div>
  )
}
