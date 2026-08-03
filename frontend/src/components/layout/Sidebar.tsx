import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Search,
  Database,
  Sparkles,
  FileText,
  Download,
  Settings as SettingsIcon,
  Radar,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/lead-finder', label: 'Lead Finder', icon: Search },
  { to: '/lead-database', label: 'Lead Database', icon: Database },
  { to: '/lead-analyzer', label: 'Lead Analyzer', icon: Sparkles },
  { to: '/audit-generator', label: 'Audit Generator', icon: FileText },
  { to: '/exports', label: 'Exports', icon: Download },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
]

export function Sidebar() {
  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-border bg-card/50">
      <div className="flex items-center gap-2 px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Radar className="h-4.5 w-4.5" />
        </div>
        <div>
          <p className="text-sm font-semibold leading-tight">AI Lead Finder</p>
          <p className="text-[11px] leading-tight text-muted-foreground">Lead intelligence</p>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 px-3">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border p-4">
        <p className="text-[11px] text-muted-foreground">
          Discovery via Google Places API. No LinkedIn scraping, no CAPTCHA bypassing.
        </p>
      </div>
    </aside>
  )
}
