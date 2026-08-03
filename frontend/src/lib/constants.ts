import type { BadgeProps } from '@/components/ui/badge'

export const BUSINESS_TYPE_PRESETS = [
  'Dentist', 'HVAC', 'Law Firm', 'Real Estate', 'Salon', 'Gym', 'Restaurant',
  'Medical Clinic', 'Veterinary', 'Accounting', 'Insurance', 'Roofing',
  'Plumbing', 'Cleaning', 'Auto Repair', 'Marketing Agency',
]

export const COUNTRIES = [
  'United States', 'Canada', 'United Kingdom', 'Ireland', 'Australia', 'New Zealand',
  'Germany', 'France', 'Spain', 'Italy', 'Netherlands', 'Belgium', 'Portugal',
  'Sweden', 'Norway', 'Denmark', 'Poland', 'Mexico', 'Brazil', 'India',
  'Singapore', 'United Arab Emirates', 'South Africa', 'Japan',
]

export const US_STATES = [
  'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
  'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
  'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
  'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
  'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina',
  'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
  'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
  'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming',
]

export const CANADA_PROVINCES = [
  'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador',
  'Nova Scotia', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan',
]

export const RADIUS_MARKS = [5, 10, 20, 30, 50, 100]

export const DECISION_MAKER_TITLES = [
  'Owner', 'Founder', 'CEO', 'President', 'Practice Manager', 'Office Manager',
  'Managing Director', 'Director', 'Manager', 'Partner', 'Managing Partner', 'Clinic Manager',
]

export const REQUIRED_INFO_FIELDS: { key: string; label: string }[] = [
  { key: 'business_name', label: 'Business Name' },
  { key: 'website', label: 'Website' },
  { key: 'phone', label: 'Phone' },
  { key: 'email', label: 'Email' },
  { key: 'address', label: 'Address' },
  { key: 'google_rating', label: 'Google Rating' },
  { key: 'google_reviews_count', label: 'Google Reviews Count' },
  { key: 'opening_hours', label: 'Opening Hours' },
  { key: 'facebook', label: 'Facebook' },
  { key: 'instagram', label: 'Instagram' },
  { key: 'linkedin_company_page', label: 'LinkedIn Company Page' },
  { key: 'decision_maker_linkedin', label: "Decision-Maker's LinkedIn (Google Search)" },
  { key: 'booking_link', label: 'Booking Link' },
  { key: 'contact_form', label: 'Contact Form' },
  { key: 'staff_page', label: 'Staff Page' },
  { key: 'about_page', label: 'About Page' },
]

export const PAIN_POINT_SEVERITY_COLOR: Record<string, BadgeProps['variant']> = {
  high: 'destructive',
  medium: 'warning',
  low: 'secondary',
}
