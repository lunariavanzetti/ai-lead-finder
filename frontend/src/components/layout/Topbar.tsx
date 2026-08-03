import { Moon, Sun, Monitor } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { useSettingsStore } from '@/store/settingsStore'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const TITLES: Record<string, string> = {
  '/': 'Dashboard',
  '/lead-finder': 'Lead Finder',
  '/lead-database': 'Lead Database',
  '/lead-analyzer': 'Lead Analyzer',
  '/audit-generator': 'Audit Generator',
  '/exports': 'Exports',
  '/settings': 'Settings',
}

const THEME_OPTIONS = [
  { value: 'light' as const, icon: Sun },
  { value: 'dark' as const, icon: Moon },
  { value: 'system' as const, icon: Monitor },
]

export function Topbar() {
  const location = useLocation()
  const theme = useSettingsStore((s) => s.theme)
  const setTheme = useSettingsStore((s) => s.setTheme)
  const title = TITLES[location.pathname] ?? 'AI Lead Finder'

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border px-6">
      <h1 className="text-sm font-semibold">{title}</h1>
      <div className="flex items-center gap-1 rounded-md border border-border p-0.5">
        {THEME_OPTIONS.map((opt) => (
          <Button
            key={opt.value}
            variant="ghost"
            size="icon"
            className={cn('h-7 w-7', theme === opt.value && 'bg-accent text-accent-foreground')}
            onClick={() => setTheme(opt.value)}
            aria-label={`${opt.value} theme`}
          >
            <opt.icon className="h-3.5 w-3.5" />
          </Button>
        ))}
      </div>
    </header>
  )
}
