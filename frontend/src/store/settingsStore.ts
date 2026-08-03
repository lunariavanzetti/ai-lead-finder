import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { AppSettings } from '@/lib/types'

interface SettingsState extends AppSettings {
  setTheme: (theme: AppSettings['theme']) => void
  setSettings: (settings: Partial<AppSettings>) => void
  applyThemeToDocument: () => void
}

function resolvePrefersDark() {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      export_folder: null,
      language: 'en',
      auto_save: true,

      setTheme: (theme) => {
        set({ theme })
        get().applyThemeToDocument()
      },

      setSettings: (settings) => {
        set(settings)
        if (settings.theme) get().applyThemeToDocument()
      },

      applyThemeToDocument: () => {
        const { theme } = get()
        const isDark = theme === 'dark' || (theme === 'system' && resolvePrefersDark())
        document.documentElement.classList.toggle('dark', isDark)
      },
    }),
    { name: 'ai-lead-finder-settings' },
  ),
)
