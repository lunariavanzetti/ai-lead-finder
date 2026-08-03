import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Pause, Play, X, CheckCircle2, Loader2, ArrowRight, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import { useJobStore } from '@/store/jobStore'
import { useJobStream } from '@/hooks/useJobStream'
import { api } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Badge, type BadgeProps } from '@/components/ui/badge'

function formatSeconds(seconds: number | null): string {
  if (seconds === null || !isFinite(seconds)) return '—'
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return m > 0 ? `${m}m ${s}s` : `${s}s`
}

export function ProgressPanel({ onNewSearch }: { onNewSearch: () => void }) {
  const navigate = useNavigate()
  const {
    activeJobId, status, businessesFound, businessesAnalyzed, emailsFound,
    websitesScanned, estimatedRemainingSeconds, currentBusiness, currentStep, logs,
  } = useJobStore()
  const [busy, setBusy] = useState(false)

  useJobStream(activeJobId)

  if (!activeJobId) return null

  const total = businessesFound || 1
  const percent = Math.min(100, Math.round((businessesAnalyzed / total) * 100))
  const isPaused = status === 'paused'
  const isDone = status === 'completed' || status === 'cancelled' || status === 'failed'

  async function handlePauseResume() {
    if (!activeJobId) return
    setBusy(true)
    try {
      if (isPaused) {
        await api.resumeJob(activeJobId)
        toast.success('Job resumed')
      } else {
        await api.pauseJob(activeJobId)
        toast.success('Job paused')
      }
    } catch {
      toast.error('Could not update job state')
    } finally {
      setBusy(false)
    }
  }

  async function handleCancel() {
    if (!activeJobId) return
    setBusy(true)
    try {
      await api.cancelJob(activeJobId)
      toast.success('Cancelling job...')
    } catch {
      toast.error('Could not cancel job')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle className="flex items-center gap-2">
          {isDone ? (
            <CheckCircle2 className="h-4.5 w-4.5 text-success" />
          ) : (
            <Loader2 className="h-4.5 w-4.5 animate-spin text-primary" />
          )}
          Scraping Progress
        </CardTitle>
        <StatusBadge status={status} />
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              {businessesAnalyzed} / {businessesFound || '…'} businesses
            </span>
            <span className="font-medium">{percent}%</span>
          </div>
          <Progress value={percent} />
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label="Businesses Found" value={businessesFound} />
          <Stat label="Analyzed" value={businessesAnalyzed} />
          <Stat label="Emails Found" value={emailsFound} />
          <Stat label="Websites Scanned" value={websitesScanned} />
        </div>

        {!isDone && (
          <div className="flex items-center justify-between rounded-md bg-muted/60 px-3 py-2 text-sm">
            <span className="truncate">
              {currentBusiness ? (
                <>
                  <span className="font-medium">{currentBusiness}</span>
                  {currentStep && <span className="text-muted-foreground"> — {currentStep}</span>}
                </>
              ) : (
                'Starting...'
              )}
            </span>
            <span className="shrink-0 text-muted-foreground">
              ETA {formatSeconds(estimatedRemainingSeconds)}
            </span>
          </div>
        )}

        <div className="rounded-md border border-border bg-muted/30">
          <p className="border-b border-border px-3 py-2 text-xs font-semibold text-muted-foreground">Live Log</p>
          <div className="scrollbar-thin max-h-40 overflow-y-auto px-3 py-2 font-mono text-xs">
            {logs.length === 0 && <p className="text-muted-foreground">Waiting for activity…</p>}
            {logs.map((line) => (
              <motion.p
                key={line.id}
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-muted-foreground"
              >
                <span className="text-primary/70">[{line.timestamp}]</span> {line.message}
              </motion.p>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {!isDone && (
            <>
              <Button variant="outline" size="sm" onClick={handlePauseResume} disabled={busy}>
                {isPaused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                {isPaused ? 'Resume' : 'Pause'}
              </Button>
              <Button variant="outline" size="sm" onClick={handleCancel} disabled={busy}>
                <X className="h-3.5 w-3.5" />
                Cancel
              </Button>
            </>
          )}
          {isDone && (
            <>
              <Button size="sm" onClick={() => navigate(`/lead-database?job_id=${activeJobId}`)}>
                View Results
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
              <Button variant="outline" size="sm" onClick={onNewSearch}>
                <RotateCcw className="h-3.5 w-3.5" />
                New Search
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border px-3 py-2.5">
      <p className="text-lg font-semibold tabular-nums">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}

const STATUS_VARIANTS: Record<string, BadgeProps['variant']> = {
  completed: 'success',
  failed: 'destructive',
  cancelled: 'destructive',
  paused: 'warning',
}

function StatusBadge({ status }: { status: string | null }) {
  if (!status) return null
  return (
    <Badge variant={STATUS_VARIANTS[status] ?? 'default'} className="capitalize">
      {status}
    </Badge>
  )
}
