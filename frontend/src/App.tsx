import { Routes, Route } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { DashboardPage } from '@/pages/DashboardPage'
import { LeadFinderPage } from '@/pages/LeadFinderPage'
import { LeadDatabasePage } from '@/pages/LeadDatabasePage'
import { LeadAnalyzerPage } from '@/pages/LeadAnalyzerPage'
import { AuditGeneratorPage } from '@/pages/AuditGeneratorPage'
import { ExportsPage } from '@/pages/ExportsPage'
import { SettingsPage } from '@/pages/SettingsPage'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/lead-finder" element={<LeadFinderPage />} />
        <Route path="/lead-database" element={<LeadDatabasePage />} />
        <Route path="/lead-analyzer" element={<LeadAnalyzerPage />} />
        <Route path="/audit-generator" element={<AuditGeneratorPage />} />
        <Route path="/exports" element={<ExportsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}

export default App
