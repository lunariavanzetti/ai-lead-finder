import { useForm } from 'react-hook-form'
import { Search } from 'lucide-react'
import { toast } from 'sonner'
import type { SearchRequest } from '@/lib/types'
import { DECISION_MAKER_TITLES } from '@/lib/constants'
import { api } from '@/lib/api'
import { useJobStore } from '@/store/jobStore'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { BusinessTypeField } from './BusinessTypeField'
import { LocationFields } from './LocationFields'
import { RadiusMaxFields } from './RadiusMaxFields'
import { DecisionMakerCheckboxes } from './DecisionMakerCheckboxes'
import { RequiredInfoCheckboxes } from './RequiredInfoCheckboxes'
import { AdvancedSettingsPanel } from './AdvancedSettingsPanel'

const DEFAULT_VALUES: SearchRequest = {
  business_type: '',
  country: 'United States',
  state: null,
  city: '',
  radius_km: 30,
  max_results: 100,
  decision_maker_titles: DECISION_MAKER_TITLES,
  required_information: {
    business_name: true, website: true, phone: true, email: true, address: true,
    google_rating: true, google_reviews_count: true, opening_hours: false,
    facebook: true, instagram: true, linkedin_company_page: true, decision_maker_linkedin: true,
    booking_link: true, contact_form: true, staff_page: true, about_page: false,
  },
  advanced_settings: {
    concurrent_workers: 6, timeout_seconds: 15, retries: 2, delay_seconds: 2.5,
    export_folder: null, proxy_url: null, rotate_user_agent: true, capture_screenshots: false,
  },
}

export function SearchForm() {
  const { register, control, handleSubmit, watch, formState } = useForm<SearchRequest>({
    defaultValues: DEFAULT_VALUES,
  })
  const startJob = useJobStore((s) => s.startJob)
  const country = watch('country')

  async function onSubmit(values: SearchRequest) {
    try {
      const { job_id } = await api.startJob(values)
      startJob(job_id, values)
      toast.success(`Started scraping ${values.business_type} in ${values.city}`)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to start job')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
      <Card>
        <CardHeader>
          <CardTitle>Search Criteria</CardTitle>
          <CardDescription>Find local businesses matching your target and location.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-6">
          <BusinessTypeField control={control} />
          <LocationFields control={control} register={register} watchCountry={country} />
          <RadiusMaxFields control={control} register={register} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Decision Maker</CardTitle>
          <CardDescription>Titles that count as a reachable decision maker for scoring.</CardDescription>
        </CardHeader>
        <CardContent>
          <DecisionMakerCheckboxes control={control} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Required Information</CardTitle>
          <CardDescription>What to collect for every lead.</CardDescription>
        </CardHeader>
        <CardContent>
          <RequiredInfoCheckboxes control={control} />
        </CardContent>
      </Card>

      <AdvancedSettingsPanel control={control} register={register} />

      <Separator />

      <div className="flex items-center justify-between">
        <Label className="font-normal text-muted-foreground">
          Discovery uses the Google Places API — no scraping of Google search pages.
        </Label>
        <Button type="submit" size="lg" disabled={formState.isSubmitting}>
          <Search className="h-4 w-4" />
          Start Scraping
        </Button>
      </div>
    </form>
  )
}
