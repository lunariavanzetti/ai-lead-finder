import { Controller, type Control, type UseFormRegister } from 'react-hook-form'
import type { SearchRequest } from '@/lib/types'
import { CANADA_PROVINCES, COUNTRIES, US_STATES } from '@/lib/constants'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export function LocationFields({
  control,
  register,
  watchCountry,
}: {
  control: Control<SearchRequest>
  register: UseFormRegister<SearchRequest>
  watchCountry: string
}) {
  const stateOptions =
    watchCountry === 'United States' ? US_STATES : watchCountry === 'Canada' ? CANADA_PROVINCES : null

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div className="flex flex-col gap-2">
        <Label>Country</Label>
        <Controller
          name="country"
          control={control}
          render={({ field }) => (
            <Select value={field.value} onValueChange={field.onChange}>
              <SelectTrigger>
                <SelectValue placeholder="Select country" />
              </SelectTrigger>
              <SelectContent>
                {COUNTRIES.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />
      </div>

      <div className="flex flex-col gap-2">
        <Label>State / Region</Label>
        {stateOptions ? (
          <Controller
            name="state"
            control={control}
            render={({ field }) => (
              <Select value={field.value ?? undefined} onValueChange={field.onChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Select state" />
                </SelectTrigger>
                <SelectContent>
                  {stateOptions.map((s) => (
                    <SelectItem key={s} value={s}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        ) : (
          <Input placeholder="e.g. Bavaria" {...register('state')} />
        )}
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="city">City</Label>
        <Input id="city" placeholder="e.g. Chicago" {...register('city', { required: true })} />
      </div>
    </div>
  )
}
