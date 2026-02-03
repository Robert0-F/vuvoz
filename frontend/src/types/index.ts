export type UserRole = 'company' | 'institution'

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
  created_at: string
}

export type RequestStatus = 'new' | 'accepted' | 'completed'

export interface CollectionRequest {
  id: number
  institution: number
  institution_name: string
  receiving_company: number
  receiving_company_name: string
  status: RequestStatus
  paper_weight_kg: string
  desired_date: string | null
  comment: string
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
  username: string
  password: string
  institution_name: string
  address: string
  contact_person: string
  phone: string
  email: string
  institution_type: string
}

export interface CreateRequestPayload {
  paper_weight_kg: string | number
  desired_date?: string | null
  comment?: string
}
