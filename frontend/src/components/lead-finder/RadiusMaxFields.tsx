import { Controller, type Control, type UseFormRegister } from 'react-hook-form'
import type { SearchRequest } from '@/lib/types'
import { RADIUS_MARKS } from '@/lib/constants'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Slider } from '@/components/ui/slider'

export function RadiusMaxFields({
  control,
  register,
}: {
  control: Control<SearchRequest>
  register: UseFormRegister<SearchRequest>
}) {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <Label>Radius</Label>
          <Controller
            name="radius_km"
            control={control}
            render={({ field }) => <span className="text-sm font-medium text-primary">{field.value} km</span>}
          />
        </div>
        <Controller
          name="radius_km"
          control={control}
          render={({ field }) => (
            <Slider
              min={5}
              max={100}
              step={5}
              value={[field.value]}
              onValueChange={(v) => field.onChange(v[0])}
            />
          )}
        />
        <div className="flex justify-between text-[11px] text-muted-foreground">
          {RADIUS_MARKS.map((m) => (
            <span key={m}>{m} km</span>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="max_results">Maximum Businesses</Label>
        <Input
          id="max_results"
          type="number"
          min={1}
          max={1000}
          {...register('max_results', { valueAsNumber: true, required: true, min: 1, max: 1000 })}
        />
      </div>
    </div>
  )
}
