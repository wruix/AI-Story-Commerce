// AI Story Commerce — Type definitions

export interface PaginationParams {
  skip?: number
  limit?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

export interface Project {
  id: string
  name: string
  description?: string
  status: "draft" | "active" | "completed" | "archived"
  customer_id?: string
  budget_cny?: number
  created_at: string
  updated_at: string
}

export interface Customer {
  id: string
  name: string
  contact_person?: string
  phone?: string
  email?: string
  company?: string
  address?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface Product {
  id: string
  project_id: string
  name: string
  category: "home_cleaning" | "daily_goods" | "apparel_warmth" | "other"
  price_cny?: number
  specifications?: string
  selling_points?: string
  target_audience?: string
  usage_scenarios?: string
  proof_materials?: string
  image_url?: string
  created_at: string
  updated_at: string
}

export interface Character {
  id: string
  name: string
  gender: "male" | "female" | "other"
  age_range?: string
  background?: string
  personality?: string
  catchphrases?: string
  worldview?: string
  commercial_boundary?: string
  reference_image_url?: string
  voice_reference_url?: string
  is_core_ip: boolean
  created_at: string
  updated_at: string
}

export interface StoryIdea {
  id: string
  product_id: string
  title: string
  description?: string
  story_type?: string
  hook?: string
  conflict?: string
  twist?: string
  product_integration?: string
  score?: number
  status: "generated" | "selected" | "rejected"
  created_at: string
}

export interface Script {
  id: string
  story_idea_id: string
  version: number
  title: string
  content: string
  raw_ai_input?: string
  raw_ai_output?: string
  status: "draft" | "approved" | "rejected" | "in_production"
  is_current: boolean
  created_at: string
}

export interface Storyboard {
  id: string
  script_id: string
  shot_number: number
  description?: string
  image_prompt?: string
  dialogue?: string
  sound_effect?: string
  duration_seconds?: number
  created_at: string
}

export interface ProductionTask {
  id: string
  storyboard_id?: string
  task_type: string
  status: "pending" | "in_progress" | "completed" | "failed"
  input_data?: string
  output_data?: string
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface MediaAsset {
  id: string
  storyboard_id?: string
  production_task_id?: string
  media_type: "image" | "video" | "audio"
  file_path: string
  sha256?: string
  file_size_bytes?: number
  duration_seconds?: number
  width?: number
  height?: number
  ai_generated: boolean
  ai_disclosure: boolean
  created_at: string
}

export interface Advertisement {
  id: string
  project_id: string
  script_id?: string
  version: number
  title: string
  file_path?: string
  sha256?: string
  duration_seconds?: number
  status: "draft" | "reviewed" | "published" | "rejected"
  is_current: boolean
  ai_disclosure: boolean
  created_at: string
}

export interface ComplianceReview {
  id: string
  advertisement_id: string
  reviewer_type: string
  ai_disclosure_required: boolean
  ai_disclosure_confirmed: boolean
  product_authenticity?: boolean
  fictional_experience_check?: boolean
  portrait_authorization?: boolean
  voice_clone_authorization?: boolean
  music_license?: boolean
  trademark_check?: boolean
  ad_content_compliance?: boolean
  status: "pending" | "passed" | "failed"
  remarks?: string
  reviewed_at?: string
  created_at: string
}

export interface PublishingRecord {
  id: string
  advertisement_id: string
  platform: "douyin" | "other"
  account_name?: string
  publish_url?: string
  publish_time?: string
  ai_disclosure_posted: boolean
  created_at: string
}

export interface PerformanceMetric {
  id: string
  publishing_record_id: string
  recorded_at: string
  views?: number
  completion_rate?: number
  likes?: number
  comments?: number
  shares?: number
  product_clicks?: number
  orders?: number
  cost_cny?: number
  cpa_cny?: number
  roas?: number
}

export interface PromptTemplate {
  id: string
  name: string
  agent_type: string
  template_content: string
  variables?: string
  version: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuditLog {
  id: string
  user_id?: string
  action: string
  resource_type?: string
  resource_id?: string
  details?: string
  ip_address?: string
  created_at: string
}
