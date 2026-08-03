import { ArrowDown, ArrowUp, ArrowUpDown, ExternalLink, Loader2 } from 'lucide-react'
import type { LeadListItem } from '@/lib/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { ScoreBadge } from './ScoreBadge'
import { cn } from '@/lib/utils'

interface LeadTableProps {
  leads: LeadListItem[]
  isLoading: boolean
  sortBy: string
  sortDir: 'asc' | 'desc'
  onSortChange: (column: string) => void
  selectedIds: Set<string>
  onToggleSelect: (id: string) => void
  onToggleSelectAll: () => void
  onRowClick: (id: string) => void
}

const columns: { key: string; label: string; sortable?: boolean }[] = [
  { key: 'lead_score', label: 'Score', sortable: true },
  { key: 'business_name', label: 'Business', sortable: true },
  { key: 'business_type', label: 'Type' },
  { key: 'owner', label: 'Decision Maker' },
  { key: 'website', label: 'Website' },
  { key: 'phone', label: 'Phone' },
  { key: 'email', label: 'Email' },
  { key: 'city', label: 'City' },
  { key: 'google_rating', label: 'Rating', sortable: true },
  { key: 'status', label: 'Status' },
]

export function LeadTable({
  leads, isLoading, sortBy, sortDir, onSortChange,
  selectedIds, onToggleSelect, onToggleSelectAll, onRowClick,
}: LeadTableProps) {
  const allSelected = leads.length > 0 && leads.every((l) => selectedIds.has(l.id))

  return (
    <div className="rounded-lg border border-border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-10">
              <Checkbox checked={allSelected} onCheckedChange={onToggleSelectAll} />
            </TableHead>
            {columns.map((col) => (
              <TableHead
                key={col.key}
                className={cn(col.sortable && 'cursor-pointer select-none')}
                onClick={() => col.sortable && onSortChange(col.key)}
              >
                <span className="inline-flex items-center gap-1">
                  {col.label}
                  {col.sortable &&
                    (sortBy === col.key ? (
                      sortDir === 'desc' ? <ArrowDown className="h-3 w-3" /> : <ArrowUp className="h-3 w-3" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 opacity-30" />
                    ))}
                </span>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading && (
            <TableRow>
              <TableCell colSpan={columns.length + 1} className="h-32 text-center">
                <Loader2 className="mx-auto h-5 w-5 animate-spin text-muted-foreground" />
              </TableCell>
            </TableRow>
          )}
          {!isLoading && leads.length === 0 && (
            <TableRow>
              <TableCell colSpan={columns.length + 1} className="h-32 text-center text-muted-foreground">
                No leads yet. Run a search from Lead Finder to populate this table.
              </TableCell>
            </TableRow>
          )}
          {!isLoading &&
            leads.map((lead) => (
              <TableRow key={lead.id} className="cursor-pointer" onClick={() => onRowClick(lead.id)}>
                <TableCell onClick={(e) => e.stopPropagation()}>
                  <Checkbox checked={selectedIds.has(lead.id)} onCheckedChange={() => onToggleSelect(lead.id)} />
                </TableCell>
                <TableCell>
                  <ScoreBadge score={lead.lead_score} />
                </TableCell>
                <TableCell className="max-w-[220px] truncate font-medium">{lead.business_name}</TableCell>
                <TableCell className="text-muted-foreground">{lead.business_type}</TableCell>
                <TableCell className="max-w-[160px] truncate">
                  {lead.owner_name ? (
                    <span>
                      {lead.owner_name}
                      {lead.owner_title && <span className="text-muted-foreground"> · {lead.owner_title}</span>}
                    </span>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell className="max-w-[180px] truncate">
                  {lead.website ? (
                    <a
                      href={lead.website}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-1 text-primary hover:underline"
                    >
                      {lead.website.replace(/^https?:\/\//, '')}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell>{lead.phone ?? <span className="text-muted-foreground">—</span>}</TableCell>
                <TableCell className="max-w-[180px] truncate">{lead.email ?? <span className="text-muted-foreground">—</span>}</TableCell>
                <TableCell>{lead.city ?? <span className="text-muted-foreground">—</span>}</TableCell>
                <TableCell>{lead.google_rating ? `${lead.google_rating}★` : <span className="text-muted-foreground">—</span>}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="capitalize">
                    {lead.status}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </div>
  )
}
