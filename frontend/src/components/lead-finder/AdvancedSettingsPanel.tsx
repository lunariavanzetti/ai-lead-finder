import { useState } from 'react'
import { Controller, type Control, type UseFormRegister } from 'react-hook-form'
import { AnimatePresence, motion } from 'framer-motion'
import { ChevronDown, SlidersHorizontal } from 'lucide-react'
import type { SearchRequest } from '@/lib/types'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { cn } from '@/lib/utils'

export function AdvancedSettingsPanel({
  control,
  register,
}: {
  control: Control<SearchRequest>
  register: UseFormRegister<SearchRequest>
}) {
  const [open, setOpen] = useState(false)

  return (
    <div className="rounded-lg border border-border">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium"
      >
        <span className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
          Advanced Settings
        </span>
        <ChevronDown className={cn('h-4 w-4 text-muted-foreground transition-transform', open && 'rotate-180')} />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="grid grid-cols-1 gap-4 border-t border-border p-4 sm:grid-cols-2 lg:grid-cols-3">
              <div className="flex flex-col gap-2">
                <Label htmlFor="concurrent_workers">Concurrent Workers</Label>
                <Input
                  id="concurrent_workers"
                  type="number"
                  min={1}
                  max={20}
                  {...register('advanced_settings.concurrent_workers', { valueAsNumber: true })}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="timeout_seconds">Timeout (seconds)</Label>
                <Input
                  id="timeout_seconds"
                  type="number"
                  min={5}
                  max={60}
                  {...register('advanced_settings.timeout_seconds', { valueAsNumber: true })}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="retries">Retries</Label>
                <Input
                  id="retries"
                  type="number"
                  min={0}
                  max={5}
                  {...register('advanced_settings.retries', { valueAsNumber: true })}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="delay_seconds">Delay Between Requests (s)</Label>
                <Input
                  id="delay_seconds"
                  type="number"
                  step={0.5}
                  min={0.5}
                  max={15}
                  {...register('advanced_settings.delay_seconds', { valueAsNumber: true })}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="export_folder">Export Folder</Label>
                <Input
                  id="export_folder"
                  placeholder="Default: backend/exported_files"
                  {...register('advanced_settings.export_folder')}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="proxy_url">Proxy URL (optional)</Label>
                <Input id="proxy_url" placeholder="http://user:pass@host:port" {...register('advanced_settings.proxy_url')} />
              </div>

              <div className="flex items-center justify-between rounded-md border border-border px-3 py-2.5 sm:col-span-1">
                <div>
                  <p className="text-sm font-medium">User Agent Rotation</p>
                  <p className="text-xs text-muted-foreground">Vary browser fingerprint per request</p>
                </div>
                <Controller
                  name="advanced_settings.rotate_user_agent"
                  control={control}
                  render={({ field }) => <Switch checked={field.value} onCheckedChange={field.onChange} />}
                />
              </div>

              <div className="flex items-center justify-between rounded-md border border-border px-3 py-2.5 sm:col-span-2">
                <div>
                  <p className="text-sm font-medium">Capture Website Screenshots</p>
                  <p className="text-xs text-muted-foreground">Slower — launches a headless browser per lead</p>
                </div>
                <Controller
                  name="advanced_settings.capture_screenshots"
                  control={control}
                  render={({ field }) => <Switch checked={field.value} onCheckedChange={field.onChange} />}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
