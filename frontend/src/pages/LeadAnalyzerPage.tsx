import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import type { LeadListItem } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { LeadDetailDrawer } from '@/components/lead-database/LeadDetailDrawer'
import { ScoreBadge } from '@/components/lead-database/ScoreBadge'

export function LeadAnalyzerPage() {
  const [businessType, setBusinessType] = useState('')
  const [openLeadId, setOpenLeadId] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['leads-analyzer', businessType],
    queryFn: () =>
      api.listLeads({ businessType: businessType || undefined, sortBy: 'lead_score', sortDir: 'desc', pageSize: 30 }),
  })

  const leads = data?.items ?? []

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-medium">Highest-Opportunity Leads</h2>
          <p className="text-xs text-muted-foreground">Ranked by automation gaps found — biggest opportunities first.</p>
        </div>
        <Input
          placeholder="Filter by business type"
          className="w-56"
          value={businessType}
          onChange={(e) => setBusinessType(e.target.value)}
        />
      </div>

      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </div>
      )}

      {!isLoading && leads.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-sm text-muted-foreground">
            No leads yet. Run a search from Lead Finder first.
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        {leads.map((lead) => (
          <LeadOpportunityCard key={lead.id} lead={lead} onOpen={() => setOpenLeadId(lead.id)} />
        ))}
      </div>

      <LeadDetailDrawer leadId={openLeadId} onOpenChange={(open) => !open && setOpenLeadId(null)} />
    </div>
  )
}

function LeadOpportunityCard({ lead, onOpen }: { lead: LeadListItem; onOpen: () => void }) {
  return (
    <Card className="cursor-pointer transition-shadow hover:shadow-md" onClick={onOpen}>
      <CardHeader className="flex-row items-start justify-between space-y-0">
        <div>
          <CardTitle className="text-sm">{lead.business_name}</CardTitle>
          <p className="text-xs text-muted-foreground">{lead.business_type}</p>
        </div>
        <ScoreBadge score={lead.lead_score} />
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div className="flex flex-wrap gap-1">
          {lead.pain_points.slice(0, 4).map((p) => (
            <Badge key={p.code} variant="destructive" className="text-[10px]">
              {p.label}
            </Badge>
          ))}
          {lead.pain_points.length > 4 && (
            <Badge variant="outline" className="text-[10px]">
              +{lead.pain_points.length - 4} more
            </Badge>
          )}
        </div>
        {lead.recommended_services.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {lead.recommended_services.slice(0, 3).map((s) => (
              <Badge key={s} variant="secondary" className="text-[10px]">
                {s}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
