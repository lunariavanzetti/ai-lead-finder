import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Moon, Sun, Monitor, Save } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '@/lib/api'
import type { AppSettings } from '@/lib/types'
import { useSettingsStore } from '@/store/settingsStore'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn } from '@/lib/utils'

const THEME_OPTIONS = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
] as const

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
]

export function SettingsPage() {
  const storeSettings = useSettingsStore()
  const [form, setForm] = useState<AppSettings>(storeSettings)
  const [saving, setSaving] = useState(false)

  const { data } = useQuery({ queryKey: ['app-settings'], queryFn: api.getSettings })

  useEffect(() => {
    if (data) setForm(data)
  }, [data])

  async function handleSave() {
    setSaving(true)
    try {
      await api.updateSettings(form)
      storeSettings.setSettings(form)
      toast.success('Settings saved')
    } catch {
      toast.error('Could not save settings')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Choose how AI Lead Finder looks.</CardDescription>
        </CardHeader>
        <CardContent>
          <RadioGroup
            className="grid grid-cols-3 gap-3"
            value={form.theme}
            onValueChange={(v) => setForm((f) => ({ ...f, theme: v as AppSettings['theme'] }))}
          >
            {THEME_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                htmlFor={`theme-${opt.value}`}
                className={cn(
                  'flex cursor-pointer flex-col items-center gap-2 rounded-lg border border-border p-4 text-sm transition-colors hover:bg-accent',
                  form.theme === opt.value && 'border-primary bg-primary/5',
                )}
              >
                <opt.icon className="h-5 w-5" />
                {opt.label}
                <RadioGroupItem id={`theme-${opt.value}`} value={opt.value} className="sr-only" />
              </label>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>General</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="export_folder">Export Folder</Label>
            <Input
              id="export_folder"
              placeholder="Default: backend/exported_files"
              value={form.export_folder ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, export_folder: e.target.value || null }))}
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label>Language</Label>
            <Select value={form.language} onValueChange={(v) => setForm((f) => ({ ...f, language: v }))}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((l) => (
                  <SelectItem key={l.value} value={l.value}>
                    {l.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between rounded-md border border-border px-3 py-2.5">
            <div>
              <p className="text-sm font-medium">Auto Save</p>
              <p className="text-xs text-muted-foreground">Persist lead status changes immediately</p>
            </div>
            <Switch checked={form.auto_save} onCheckedChange={(v) => setForm((f) => ({ ...f, auto_save: v }))} />
          </div>
        </CardContent>
      </Card>

      <Button onClick={handleSave} disabled={saving} className="w-fit">
        <Save className="h-4 w-4" />
        Save Settings
      </Button>
    </div>
  )
}
