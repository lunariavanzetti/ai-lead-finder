import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, History } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '@/lib/api'
import type { ExportFormat } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'

const FORMATS: { value: ExportFormat; label: string; description: string }[] = [
  { value: 'csv', label: 'CSV', description: 'Universal spreadsheet format' },
  { value: 'xlsx', label: 'Excel', description: 'Formatted workbook with styled headers' },
  { value: 'json', label: 'JSON', description: 'Full nested data, incl. staff and scoring breakdown' },
  { value: 'sqlite', label: 'SQLite', description: 'Portable database file' },
]

export function ExportsPage() {
  const [jobId, setJobId] = useState<string>('all')
  const [format, setFormat] = useState<ExportFormat>('csv')
  const [busy, setBusy] = useState(false)

  const { data: jobs } = useQuery({ queryKey: ['jobs'], queryFn: () => api.listJobs(30) })
  const { data: history } = useQuery({ queryKey: ['search-history'], queryFn: api.getSearchHistory })

  async function handleExport() {
    setBusy(true)
    try {
      await api.exportLeads(format, { jobId: jobId === 'all' ? undefined : jobId })
      toast.success(`Export started (${format.toUpperCase()})`)
    } catch {
      toast.error('Export failed — try a different scope or format')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Export Leads</CardTitle>
          <CardDescription>Download leads from a specific search, or your entire database.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label>Scope</Label>
              <Select value={jobId} onValueChange={setJobId}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All leads</SelectItem>
                  {jobs?.map((job) => (
                    <SelectItem key={job.id} value={job.id}>
                      {job.params.business_type} — {job.params.city} ({job.businesses_analyzed})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {FORMATS.map((f) => (
              <button
                key={f.value}
                onClick={() => setFormat(f.value)}
                className={`rounded-lg border p-3 text-left transition-colors ${
                  format === f.value ? 'border-primary bg-primary/5' : 'border-border hover:bg-accent'
                }`}
              >
                <p className="text-sm font-semibold">{f.label}</p>
                <p className="text-xs text-muted-foreground">{f.description}</p>
              </button>
            ))}
          </div>

          <Button onClick={handleExport} disabled={busy} className="w-fit">
            <Download className="h-4 w-4" />
            Export {format.toUpperCase()}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Search History
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          {history?.length === 0 && <p className="text-sm text-muted-foreground">No searches yet.</p>}
          {history?.map((h) => (
            <div key={h.id} className="flex items-center justify-between rounded-md border border-border px-3 py-2.5 text-sm">
              <div>
                <p className="font-medium">{h.business_type}</p>
                <p className="text-xs text-muted-foreground">{h.location_label}</p>
              </div>
              <Badge variant="outline">{h.result_count} results</Badge>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
