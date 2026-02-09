export type UserRole = 'admin' | 'company' | 'institution'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  role_display: string
}

export interface CompanyProfile {
  id: number
  company_name: string
  address: string
  contact_phone: string
  contact_email: string
  legal_address?: string
  inn?: string
  kpp?: string
  ogrn?: string
  bank_account?: string
  bank_name?: string
  bik?: string
  corr_account?: string
  website?: string
  logo?: string
  description?: string
  created_at: string
}

export interface InstitutionProfile {
  id: number
  parent_company: number
  parent_company_name: string
  institution_name: string
  address: string
  contact_person: string
  phone: string
  email: string
  institution_type: string
  legal_address?: string
  inn?: string
  kpp?: string
  contact_person_on_site?: string
  phone_on_site?: string
  preferred_days?: string
  preferred_hours?: string
  access_details?: string
  container_location?: string
  created_at: string
}

export type RequestStatus = 'new' | 'accepted' | 'completed'
export type Urgency = 'low' | 'medium' | 'high'
export type MaterialType = 'paper' | 'cardboard' | 'newspapers' | 'mixed' | 'archive'

export interface CollectionRequest {
  id: number
  request_number?: string
  institution: number
  institution_name: string
  receiving_company: number
  receiving_company_name: string
  status: RequestStatus
  urgency?: Urgency
  material_type?: MaterialType
  material_type_display?: string
  paper_weight_kg: string
  estimated_amount?: string
  actual_amount?: string | null
  estimated_value?: string
  actual_value?: string | null
  desired_date: string | null
  estimated_collection_date?: string | null
  actual_collection_date?: string | null
  comment: string
  notes?: string
  internal_notes?: string
  created_at: string
  completed_at?: string | null
}

export interface Notification {
  id: number
  title: string
  message: string
  link: string
  read: boolean
  created_at: string
}

export interface CurrentUserResponse {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  role_display: string
  profile: CompanyProfile | InstitutionProfile | null
}

export interface TokenResponse {
  access: string
  refresh: string
}

export interface CreateInstitutionPayload {
  email: string
  password?: string
  institution_name: string
  address: string
  contact_person: string
  phone: string
  institution_type: string
}

export interface CreateRequestPayload {
  material_type?: MaterialType
  estimated_amount?: string | number
  paper_weight_kg?: string | number
  urgency?: Urgency
  desired_date?: string | null
  comment?: string
}

export interface CurrentPrice {
  material_type: string
  material_type_display: string
  price_per_kg: string
}

export interface PriceList {
  id: number
  material_type: string
  material_type_display: string
  price_per_kg: string
  valid_from: string
  valid_to: string | null
  is_active: boolean
  created_at: string
}

export interface NewsArticle {
  id: number
  title: string
  content: string
  excerpt: string
  image: string | null
  image_url: string | null
  created_at: string
  is_published: boolean
  author: number | null
  author_username: string
}

export interface CompleteRequestPayload {
  actual_amount: string | number
  actual_collection_date?: string | null
  internal_notes?: string
}
