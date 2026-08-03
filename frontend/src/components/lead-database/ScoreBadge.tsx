import { cn } from '@/lib/utils'

export function ScoreBadge({ score, className }: { score: number; className?: string }) {
  const tone =
    score >= 70 ? 'bg-success/15 text-success' : score >= 40 ? 'bg-warning/15 text-warning' : 'bg-muted text-muted-foreground'

  return (
    <span className={cn('inline-flex h-7 w-11 items-center justify-center rounded-md text-xs font-semibold tabular-nums', tone, className)}>
      {score}
    </span>
  )
}
