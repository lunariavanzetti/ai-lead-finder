import { Controller, type Control } from 'react-hook-form'
import type { SearchRequest } from '@/lib/types'
import { BUSINESS_TYPE_PRESETS } from '@/lib/constants'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'

export function BusinessTypeField({ control }: { control: Control<SearchRequest> }) {
  return (
    <Controller
      name="business_type"
      control={control}
      rules={{ required: true, minLength: 2 }}
      render={({ field }) => (
        <div className="flex flex-col gap-2">
          <Label htmlFor="business_type">Business Type</Label>
          <Input
            id="business_type"
            placeholder="e.g. Dentist, or type your own"
            {...field}
          />
          <div className="flex flex-wrap gap-1.5">
            {BUSINESS_TYPE_PRESETS.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => field.onChange(preset)}
                className={cn(
                  'rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground',
                  field.value === preset && 'border-primary bg-primary/10 text-primary',
                )}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      )}
    />
  )
}
