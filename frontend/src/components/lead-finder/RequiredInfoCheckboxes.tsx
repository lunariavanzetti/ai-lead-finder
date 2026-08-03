import { Controller, type Control } from 'react-hook-form'
import type { RequiredInformation, SearchRequest } from '@/lib/types'
import { REQUIRED_INFO_FIELDS } from '@/lib/constants'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'

export function RequiredInfoCheckboxes({ control }: { control: Control<SearchRequest> }) {
  return (
    <Controller
      name="required_information"
      control={control}
      render={({ field }) => {
        const value = field.value
        const toggle = (key: keyof RequiredInformation) => {
          field.onChange({ ...value, [key]: !value[key] })
        }
        return (
          <div className="grid grid-cols-2 gap-x-6 gap-y-2.5 sm:grid-cols-3">
            {REQUIRED_INFO_FIELDS.map(({ key, label }) => (
              <label key={key} className="flex cursor-pointer items-center gap-2 text-sm">
                <Checkbox
                  checked={value[key as keyof RequiredInformation]}
                  onCheckedChange={() => toggle(key as keyof RequiredInformation)}
                />
                <Label className="cursor-pointer font-normal">{label}</Label>
              </label>
            ))}
          </div>
        )
      }}
    />
  )
}
