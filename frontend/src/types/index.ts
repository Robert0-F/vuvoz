export type UserRole = 'admin' | 'company' | 'institution' | 'support'

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
  parent_company_contact_phone?: string
  parent_company_contact_email?: string
  support_user?: number | null
  support_username?: string
  institution_name: string
  address: string
  contact_person: string
  phone: string
  email: string
  institution_type: string
  bonus_balance?: string
  support_unread_count?: number
  legal_address?: string
  inn?: string
  kpp?: string
  contact_person_on_site?: string
  phone_on_site?: string
  preferred_days?: string
  preferred_hours?: string
  access_details?: string
  container_location?: string
  company_notes?: string
  created_at: string
}

export interface SupportAssignedInstitution {
  id: number
  institution_name: string
  address: string
  contact_person: string
  phone: string
  email: string
  unread_count?: number
  last_message_at?: string | null
  last_message_preview?: string
}

export interface SupportConfig {
  id: number
  support_user: number | null
  support_username: string
  support_email: string
  institutions_assigned: number
}

export interface SupportProfile {
  institutions: SupportAssignedInstitution[]
}

export interface SupportChatMessage {
  id: number
  institution: number
  sender: number
  sender_username: string
  sender_role: UserRole
  message: string
  is_read: boolean
  is_mine?: boolean
  created_at: string
}

export interface ProductCategory {
  id: number
  name: string
  slug: string
  sort_order: number
  is_active: boolean
  product_count?: number
}

export interface Product {
  id: number
  category: number | null
  category_name?: string | null
  category_slug?: string | null
  name: string
  description: string
  price_in_points: string
  is_active: boolean
  image_url?: string | null
  created_at: string
}

export interface PublicProduct {
  id: number
  name: string
  description: string
  price_in_points: string
  image_url?: string | null
  category_id: number | null
  category_name: string | null
  category_slug: string | null
}

export interface PointsHistoryItem {
  type: 'accrual' | 'expense'
  amount: string
  date: string | null
  reference: string
}

export type RequestStatus = 'new' | 'accepted' | 'pending_confirmation' | 'completed' | 'cancelled'
export type Urgency = 'low' | 'medium' | 'high'
/** Material code (e.g. cardboard, paper). New codes can be added via admin. */
export type MaterialType = string

export interface CollectionRequest {
  id: number
  request_number?: string
  institution: number
  institution_name: string
  receiving_company: number
  receiving_company_name: string
  receiving_company_phone?: string
  receiving_company_email?: string
  status: RequestStatus
  urgency?: Urgency
  material_type?: MaterialType
  material_type_display?: string
  material_lines?: { material_type: string; amount_kg: string }[]
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
  profile: CompanyProfile | InstitutionProfile | SupportProfile | null
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

export interface Material {
  id: number
  name: string
  code: string
  short_description?: string
  icon_url?: string | null
  image_url?: string | null
  icon?: string
  sort_order?: number
  is_active: boolean
}

export interface PublicMaterial {
  id: number
  code: string
  name: string
  short_description: string
  icon: string
  icon_url: string | null
  image_url: string | null
  price_per_kg: string
  sort_order: number
}

export type PublicPickupStatus = 'new' | 'contacted' | 'done' | 'cancelled'

export interface PublicPickupRequestLine {
  id: number
  material: number
  material_name: string
  material_code: string
  weight_kg: string
  line_payout: string
}

export interface PublicPickupRequest {
  id: number
  contact_name: string
  phone: string
  address: string
  preferred_date: string
  lines: PublicPickupRequestLine[]
  materials_summary: string
  total_weight_kg: string
  estimated_payout: string
  status: PublicPickupStatus
  status_display: string
  admin_notes: string
  created_at: string
}

export interface InstitutionRegistrationRequest {
  id: number
  first_name: string
  patronymic: string
  institution_name: string
  address: string
  phone: string
  email: string
  created_at: string
}

export interface CompanyRegistrationRequest {
  id: number
  company_name: string
  contact_name: string
  phone: string
  email: string
  address: string
  comment: string
  created_at: string
}

export interface PriceList {
  id: number
  material: number
  material_code: string
  material_name: string
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
