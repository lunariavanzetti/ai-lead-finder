import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Globe, Phone, Mail, MapPin, Star, Calendar,
  FileDown, ExternalLink, Loader2, Clock, Check,
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '@/lib/api'
import { PAIN_POINT_SEVERITY_COLOR } from '@/lib/constants'
import { FacebookIcon, InstagramIcon, LinkedinIcon } from '@/components/icons/BrandIcons'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ScoreBadge } from './ScoreBadge'
import { MessageBlock } from './MessageBlock'

const STATUS_OPTIONS = ['new', 'reviewed', 'contacted', 'archived']

const TECH_LABELS: Record<string, string> = {
  live_chat: 'Live Chat', chatbot: 'Chatbot', booking_system: 'Booking System',
  faq: 'FAQ', ssl: 'SSL', mobile_friendly: 'Mobile Friendly',
  facebook_pixel: 'Facebook Pixel', google_analytics: 'Google Analytics',
  crm: 'CRM', newsletter: 'Newsletter', google_reviews_widget: 'Reviews Widget',
  instagram_feed: 'Instagram Feed',
}

export function LeadDetailDrawer({ leadId, onOpenChange }: { leadId: string | null; onOpenChange: (open: boolean) => void }) {
  const queryClient = useQueryClient()
  const { data: lead, isLoading } = useQuery({
    queryKey: ['lead', leadId],
    queryFn: () => api.getLead(leadId as string),
    enabled: !!leadId,
  })

  async function handleStatusChange(status: string) {
    if (!leadId) return
    await api.updateLeadStatus(leadId, status)
    queryClient.invalidateQueries({ queryKey: ['lead', leadId] })
    queryClient.invalidateQueries({ queryKey: ['leads'] })
    toast.success('Status updated')
  }

  async function handleExportAudit() {
    if (!lead) return
    try {
      await api.exportAudit(lead.id, lead.business_name)
      toast.success('Audit PDF downloaded')
    } catch {
      toast.error('Could not generate audit PDF')
    }
  }

  return (
    <Sheet open={!!leadId} onOpenChange={onOpenChange}>
      <SheetContent widthClassName="w-full sm:max-w-xl">
        {isLoading && (
          <div className="flex h-full items-center justify-center">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        )}

        {lead && (
          <>
            <SheetHeader>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <SheetTitle>{lead.business_name}</SheetTitle>
                  <SheetDescription>{lead.business_type}</SheetDescription>
                </div>
                <ScoreBadge score={lead.lead_score} className="h-10 w-14 text-base" />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <Select value={lead.status} onValueChange={handleStatusChange}>
                  <SelectTrigger className="h-8 w-36 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {STATUS_OPTIONS.map((s) => (
                      <SelectItem key={s} value={s} className="capitalize">
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button size="sm" variant="outline" onClick={handleExportAudit}>
                  <FileDown className="h-3.5 w-3.5" />
                  Export Audit PDF
                </Button>
              </div>
            </SheetHeader>

            <div className="flex flex-col gap-6 p-5">
              <section className="flex flex-col gap-2 text-sm">
                {lead.website && <InfoRow icon={Globe} value={lead.website} href={lead.website} />}
                {lead.phone && <InfoRow icon={Phone} value={lead.phone} />}
                {lead.email && <InfoRow icon={Mail} value={lead.email} href={`mailto:${lead.email}`} />}
                {lead.address && <InfoRow icon={MapPin} value={[lead.address, lead.city, lead.state, lead.country].filter(Boolean).join(', ')} />}
                {lead.google_rating && (
                  <InfoRow icon={Star} value={`${lead.google_rating} (${lead.google_reviews_count ?? 0} reviews)`} href={lead.google_maps_url ?? undefined} />
                )}
                {lead.booking_link && <InfoRow icon={Calendar} value="Has booking link" href={lead.booking_link} />}
                {lead.estimated_hours_saved_per_week && (
                  <InfoRow icon={Clock} value={`~${lead.estimated_hours_saved_per_week} hrs/week estimated savings`} />
                )}
                <div className="flex gap-3 pt-1">
                  {lead.facebook_url && <SocialIcon icon={FacebookIcon} href={lead.facebook_url} />}
                  {lead.instagram_url && <SocialIcon icon={InstagramIcon} href={lead.instagram_url} />}
                  {lead.linkedin_company_url && <SocialIcon icon={LinkedinIcon} href={lead.linkedin_company_url} />}
                </div>
              </section>

              {lead.crawl_error && (
                <p className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">
                  Crawl issue: {lead.crawl_error}
                </p>
              )}

              <Separator />

              <section>
                <h4 className="mb-2 text-sm font-semibold">Staff / Decision Makers</h4>
                {lead.staff.length === 0 && <p className="text-sm text-muted-foreground">No staff found on the site.</p>}
                <div className="flex flex-col gap-2">
                  {lead.staff.map((s) => (
                    <div key={s.id} className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm">
                      <div>
                        <p className="font-medium">{s.full_name}</p>
                        <p className="text-xs text-muted-foreground">{s.title ?? '—'}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {s.linkedin_url && <SocialIcon icon={LinkedinIcon} href={s.linkedin_url} />}
                        {s.is_decision_maker && <Badge variant="default">Decision Maker</Badge>}
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              <Separator />

              {lead.strengths.length > 0 && (
                <>
                  <section>
                    <h4 className="mb-2 text-sm font-semibold">Strengths</h4>
                    <div className="flex flex-col gap-1.5">
                      {lead.strengths.map((s) => (
                        <div key={s} className="flex items-center gap-2 text-sm">
                          <Check className="h-3.5 w-3.5 shrink-0 text-success" />
                          <span>{s}</span>
                        </div>
                      ))}
                    </div>
                  </section>
                  <Separator />
                </>
              )}

              <section>
                <h4 className="mb-2 text-sm font-semibold">Detected Problems</h4>
                <div className="flex flex-col gap-1.5">
                  {lead.pain_points.map((p) => (
                    <div key={p.code} className="flex items-center gap-2 text-sm">
                      <Badge variant={PAIN_POINT_SEVERITY_COLOR[p.severity]} className="w-16 shrink-0 justify-center capitalize">
                        {p.severity}
                      </Badge>
                      <span>{p.label}</span>
                    </div>
                  ))}
                  {lead.pain_points.length === 0 && <p className="text-sm text-muted-foreground">No significant gaps detected.</p>}
                </div>
              </section>

              <Separator />

              <section>
                <h4 className="mb-2 text-sm font-semibold">Suggested Offer</h4>
                <div className="flex flex-wrap gap-1.5">
                  {lead.recommended_services.map((s) => (
                    <Badge key={s} variant="secondary">
                      {s}
                    </Badge>
                  ))}
                  {lead.recommended_services.length === 0 && <p className="text-sm text-muted-foreground">Nothing to recommend.</p>}
                </div>
              </section>

              {(lead.outreach_message || lead.follow_up_message) && (
                <>
                  <Separator />
                  <section className="flex flex-col gap-4">
                    {lead.outreach_message && (
                      <MessageBlock title="Suggested Outreach Message" message={lead.outreach_message} />
                    )}
                    {lead.follow_up_message && (
                      <MessageBlock title="Suggested Follow-Up Message" message={lead.follow_up_message} />
                    )}
                  </section>
                </>
              )}

              {lead.discovery_questions.length > 0 && (
                <>
                  <Separator />
                  <section>
                    <h4 className="mb-2 text-sm font-semibold">Discovery Call Questions</h4>
                    <ol className="flex list-decimal flex-col gap-1.5 pl-4 text-sm">
                      {lead.discovery_questions.map((q) => (
                        <li key={q}>{q}</li>
                      ))}
                    </ol>
                  </section>
                </>
              )}

              <Separator />

              <section>
                <h4 className="mb-2 text-sm font-semibold">Detected Technologies</h4>
                <div className="flex flex-wrap gap-1.5">
                  {Object.entries(TECH_LABELS).map(([key, label]) => {
                    const detected = Boolean(lead.technologies?.[key])
                    return (
                      <Badge key={key} variant={detected ? 'success' : 'outline'} className="text-[11px]">
                        {label}
                      </Badge>
                    )
                  })}
                </div>
              </section>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  )
}

function InfoRow({ icon: Icon, value, href }: { icon: React.ComponentType<{ className?: string }>; value: string; href?: string }) {
  const content = (
    <span className="flex items-center gap-2">
      <Icon className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
      <span className="truncate">{value}</span>
    </span>
  )
  if (!href) return <div className="text-foreground">{content}</div>
  return (
    <a href={href} target="_blank" rel="noreferrer" className="flex items-center justify-between text-foreground hover:text-primary">
      {content}
      <ExternalLink className="h-3 w-3 shrink-0 text-muted-foreground" />
    </a>
  )
}

function SocialIcon({ icon: Icon, href }: { icon: React.ComponentType<{ className?: string }>; href: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="flex h-8 w-8 items-center justify-center rounded-md border border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground"
    >
      <Icon className="h-4 w-4" />
    </a>
  )
}
