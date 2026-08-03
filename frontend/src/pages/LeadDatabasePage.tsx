import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Download, Search, X } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '@/lib/api'
import type { ExportFormat } from '@/lib/types'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { LeadTable } from '@/components/lead-database/LeadTable'
import { LeadDetailDrawer } from '@/components/lead-database/LeadDetailDrawer'

const PAGE_SIZE = 25
const EXPORT_FORMATS: ExportFormat[] = ['csv', 'xlsx', 'json', 'sqlite']

export function LeadDatabasePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const jobId = searchParams.get('job_id') ?? undefined

  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [sortBy, setSortBy] = useState('lead_score')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [openLeadId, setOpenLeadId] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['leads', { jobId, search, page, sortBy, sortDir }],
    queryFn: () =>
      api.listLeads({ jobId, search: search || undefined, page, pageSize: PAGE_SIZE, sortBy, sortDir }),
  })

  const leads = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const selectionSummary = useMemo(() => `${selectedIds.size} selected`, [selectedIds])

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  function toggleSelectAll() {
    setSelectedIds((prev) => {
      if (leads.every((l) => prev.has(l.id))) return new Set()
      return new Set(leads.map((l) => l.id))
    })
  }

  function handleSortChange(column: string) {
    if (sortBy === column) {
      setSortDir((d) => (d === 'desc' ? 'asc' : 'desc'))
    } else {
      setSortBy(column)
      setSortDir('desc')
    }
  }

  async function handleExport(format: ExportFormat, scope: 'selected' | 'all') {
    try {
      await api.exportLeads(format, {
        jobId: scope === 'all' ? jobId : undefined,
        leadIds: scope === 'selected' ? Array.from(selectedIds) : undefined,
      })
      toast.success(`Exported ${scope === 'selected' ? selectedIds.size : total} leads as ${format.toUpperCase()}`)
    } catch {
      toast.error('Export failed')
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="relative w-72">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search business, email, website..."
            className="pl-8"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
          />
        </div>

        <div className="flex items-center gap-2">
          {jobId && (
            <Button variant="outline" size="sm" onClick={() => setSearchParams({})}>
              <X className="h-3.5 w-3.5" />
              Clear job filter
            </Button>
          )}
          {selectedIds.size > 0 && (
            <ExportDropdown label={`Export Selected (${selectedIds.size})`} onExport={(f) => handleExport(f, 'selected')} />
          )}
          <ExportDropdown label="Export All" onExport={(f) => handleExport(f, 'all')} />
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <LeadTable
            leads={leads}
            isLoading={isLoading}
            sortBy={sortBy}
            sortDir={sortDir}
            onSortChange={handleSortChange}
            selectedIds={selectedIds}
            onToggleSelect={toggleSelect}
            onToggleSelectAll={toggleSelectAll}
            onRowClick={setOpenLeadId}
          />
        </CardContent>
      </Card>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          {total} leads {selectedIds.size > 0 && `· ${selectionSummary}`}
        </span>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Previous
          </Button>
          <span>
            Page {page} / {totalPages}
          </span>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
            Next
          </Button>
        </div>
      </div>

      <LeadDetailDrawer leadId={openLeadId} onOpenChange={(open) => !open && setOpenLeadId(null)} />
    </div>
  )
}

function ExportDropdown({ label, onExport }: { label: string; onExport: (format: ExportFormat) => void }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          <Download className="h-3.5 w-3.5" />
          {label}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {EXPORT_FORMATS.map((format) => (
          <DropdownMenuItem key={format} onClick={() => onExport(format)} className="uppercase">
            {format}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
