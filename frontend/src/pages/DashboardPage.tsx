import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Users, Briefcase, TrendingUp, Target, ArrowRight } from 'lucide-react'
import { api } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ['dashboard'], queryFn: api.getDashboardStats })

  const stats = [
    { label: 'Total Leads', value: data?.total_leads ?? 0, icon: Users },
    { label: 'Searches Run', value: data?.total_jobs ?? 0, icon: Briefcase },
    { label: 'Avg. Lead Score', value: data?.average_lead_score ?? 0, icon: TrendingUp },
    { label: 'High Priority (70+)', value: data?.high_priority_leads ?? 0, icon: Target },
  ]

  const maxPainCount = Math.max(1, ...(data?.top_pain_points.map((p) => p.count) ?? [1]))

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label}>
            <CardContent className="flex items-center justify-between p-5">
              <div>
                <p className="text-xs text-muted-foreground">{s.label}</p>
                <p className="text-2xl font-semibold tabular-nums">{isLoading ? '—' : s.value}</p>
              </div>
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <s.icon className="h-4.5 w-4.5" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Most Common Automation Gaps</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {data?.top_pain_points.length === 0 && (
              <p className="text-sm text-muted-foreground">Run a search to see trends across your leads.</p>
            )}
            {data?.top_pain_points.map((p) => (
              <div key={p.label} className="flex flex-col gap-1">
                <div className="flex items-center justify-between text-sm">
                  <span>{p.label}</span>
                  <span className="text-muted-foreground">{p.count}</span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{ width: `${(p.count / maxPainCount) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Searches</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            {data?.recent_jobs.length === 0 && (
              <p className="text-sm text-muted-foreground">No searches yet.</p>
            )}
            {data?.recent_jobs.map((job) => (
              <Link
                key={job.id}
                to={`/lead-database?job_id=${job.id}`}
                className="flex items-center justify-between rounded-md border border-border px-3 py-2.5 text-sm transition-colors hover:bg-accent"
              >
                <div>
                  <p className="font-medium">
                    {job.business_type ?? 'Search'} {job.city && `— ${job.city}`}
                  </p>
                  <p className="text-xs text-muted-foreground">{job.businesses_analyzed} businesses analyzed</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="capitalize">
                    {job.status}
                  </Badge>
                  <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card className="border-dashed">
        <CardContent className="flex items-center justify-between p-5">
          <div>
            <p className="text-sm font-medium">Ready to find more leads?</p>
            <p className="text-xs text-muted-foreground">Search a new business type or location.</p>
          </div>
          <Button asChild>
            <Link to="/lead-finder">
              Open Lead Finder
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
