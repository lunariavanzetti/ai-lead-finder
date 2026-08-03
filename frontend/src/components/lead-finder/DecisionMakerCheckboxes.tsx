import { Controller, type Control } from 'react-hook-form'
import type { SearchRequest } from '@/lib/types'
import { DECISION_MAKER_TITLES } from '@/lib/constants'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'

export function DecisionMakerCheckboxes({ control }: { control: Control<SearchRequest> }) {
  return (
    <Controller
      name="decision_maker_titles"
      control={control}
      render={({ field }) => {
        const selected = new Set(field.value)
        const toggle = (title: string) => {
          const next = new Set(selected)
          next.has(title) ? next.delete(title) : next.add(title)
          field.onChange(Array.from(next))
        }
        return (
          <div className="grid grid-cols-2 gap-x-6 gap-y-2.5 sm:grid-cols-3">
            {DECISION_MAKER_TITLES.map((title) => (
              <label key={title} className="flex cursor-pointer items-center gap-2 text-sm">
                <Checkbox checked={selected.has(title)} onCheckedChange={() => toggle(title)} />
                <Label className="cursor-pointer font-normal">{title}</Label>
              </label>
            ))}
          </div>
        )
      }}
    />
  )
}
