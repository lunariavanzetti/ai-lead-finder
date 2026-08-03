import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileDown, Search, Clock, Check } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '@/lib/api'
import type { LeadDetail } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ScoreBadge } from '@/components/lead-database/ScoreBadge'
import { MessageBlock } from '@/components/lead-database/MessageBlock'
import { PAIN_POINT_SEVERITY_COLOR } from '@/lib/constants'
import { cn } from '@/lib/utils'

export function AuditGeneratorPage() {
  const [search, setSearch] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const { data } = useQuery({
    queryKey: ['leads-audit', search],
    queryFn: () => api.listLeads({ search: search || undefined, sortBy: 'lead_score', sortDir: 'desc', pageSize: 30 }),
  })
  const leads = data?.items ?? []

  const { data: lead } = useQuery({
    queryKey: ['lead', selectedId],
    queryFn: () => api.getLead(selectedId as string),
    enabled: !!selectedId,
  })

  async function handleDownload() {
    if (!lead) return
    try {
      await api.exportAudit(lead.id, lead.business_name)
      toast.success('Audit PDF downloaded')
    } catch {
      toast.error('Could not generate audit PDF')
    }
  }

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">
      <Card className="h-fit">
        <CardHeader>
          <CardTitle>Select a Business</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Search leads..." className="pl-8" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <div className="scrollbar-thin flex max-h-[480px] flex-col gap-1 overflow-y-auto">
            {leads.map((l) => (
              <button
                key={l.id}
                onClick={() => setSelectedId(l.id)}
                className={cn(
                  'flex items-center justify-between rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent',
                  selectedId === l.id && 'bg-accent',
                )}
              >
                <span className="truncate">{l.business_name}</span>
                <ScoreBadge score={l.lead_score} className="h-6 w-9 text-[11px]" />
              </button>
            ))}
            {leads.length === 0 && <p className="px-3 py-2 text-sm text-muted-foreground">No leads found.</p>}
          </div>
        </CardContent>
      </Card>

      {!lead && (
        <Card>
          <CardContent className="flex h-full items-center justify-center p-16 text-center text-sm text-muted-foreground">
            Select a business on the left to preview its audit.
          </CardContent>
        </Card>
      )}

      {lead && (
        <Card>
          <CardHeader className="flex-row items-start justify-between space-y-0">
            <div>
              <CardTitle className="text-xl">AI Automation Audit</CardTitle>
              <CardDescription>{lead.business_name}</CardDescription>
            </div>
            <Button onClick={handleDownload}>
              <FileDown className="h-4 w-4" />
              Download PDF
            </Button>
          </CardHeader>
          <CardContent className="flex flex-col gap-6">
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-3">
              <InfoField label="Business Type" value={lead.business_type} />
              <InfoField label="Website" value={lead.website ?? '—'} />
              <InfoField label="Phone" value={lead.phone ?? '—'} />
              <InfoField label="Email" value={lead.email ?? '—'} />
              <InfoField
                label="Address"
                value={[lead.address, lead.city, lead.state, lead.country].filter(Boolean).join(', ') || '—'}
              />
              <InfoField
                label="Decision Maker"
                value={lead.owner_name ? `${lead.owner_name}${lead.owner_title ? ` (${lead.owner_title})` : ''}` : '—'}
              />
              {primaryLinkedIn(lead) && <InfoField label="LinkedIn" value={primaryLinkedIn(lead) as string} />}
            </div>

            <Separator />

            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-muted-foreground">Lead / Opportunity Score</span>
              <span className="text-3xl font-bold text-primary">{lead.lead_score}/100</span>
            </div>

            <Separator />

            {lead.strengths.length > 0 && (
              <div>
                <h4 className="mb-2 text-sm font-semibold">Strengths</h4>
                <div className="flex flex-col gap-1.5">
                  {lead.strengths.map((s) => (
                    <div key={s} className="flex items-center gap-2 text-sm">
                      <Check className="h-3.5 w-3.5 shrink-0 text-success" />
                      <span>{s}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <Separator />

            <div>
              <h4 className="mb-2 text-sm font-semibold">Detected Problems</h4>
              <div className="flex flex-col gap-1.5">
                {lead.pain_points.map((p) => (
                  <div key={p.code} className="flex items-center gap-2 text-sm">
                    <Badge variant={PAIN_POINT_SEVERITY_COLOR[p.severity]} className="w-16 shrink-0 justify-center capitalize">
                      {p.severity}
                    </Badge>
                    {p.label}
                  </div>
                ))}
                {lead.pain_points.length === 0 && <p className="text-sm text-muted-foreground">No significant gaps detected.</p>}
              </div>
            </div>

            <Separator />

            <div>
              <h4 className="mb-2 text-sm font-semibold">Recommended Solutions</h4>
              <div className="flex flex-wrap gap-1.5">
                {lead.recommended_services.map((s) => (
                  <Badge key={s} variant="secondary">
                    {s}
                  </Badge>
                ))}
              </div>
            </div>

            {lead.estimated_hours_saved_per_week && (
              <>
                <Separator />
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  Estimated time saved: <span className="font-medium">{lead.estimated_hours_saved_per_week} hours / week</span>
                </div>
              </>
            )}

            {(lead.outreach_message || lead.follow_up_message) && (
              <>
                <Separator />
                <div className="flex flex-col gap-4">
                  {lead.outreach_message && <MessageBlock title="Suggested Outreach Message" message={lead.outreach_message} />}
                  {lead.follow_up_message && <MessageBlock title="Suggested Follow-Up Message" message={lead.follow_up_message} />}
                </div>
              </>
            )}

            {lead.discovery_questions.length > 0 && (
              <>
                <Separator />
                <div>
                  <h4 className="mb-2 text-sm font-semibold">Discovery Call Questions</h4>
                  <ol className="flex list-decimal flex-col gap-1.5 pl-4 text-sm">
                    {lead.discovery_questions.map((q) => (
                      <li key={q}>{q}</li>
                    ))}
                  </ol>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function primaryLinkedIn(lead: LeadDetail): string | null {
  const decisionMakers = lead.staff.filter((s) => s.is_decision_maker)
  const pool = decisionMakers.length > 0 ? decisionMakers : lead.staff
  const contact = [...pool].sort((a, b) => a.priority_rank - b.priority_rank)[0]
  return contact?.linkedin_url ?? null
}

function InfoField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="truncate font-medium">{value}</p>
    </div>
  )
}
