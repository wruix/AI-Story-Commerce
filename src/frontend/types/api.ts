// AI Story Commerce — Create/Update types

export interface ProjectCreate {
  name: string
  description?: string
  customer_id?: string
  budget_cny?: number
}

export interface ProjectUpdate {
  name?: string
  description?: string
  status?: "draft" | "active" | "completed" | "archived"
  customer_id?: string
  budget_cny?: number
}

export interface CustomerCreate {
  name: string
  contact_person?: string
  phone?: string
  email?: string
  company?: string
  address?: string
  notes?: string
}

export interface CustomerUpdate {
  name?: string
  contact_person?: string
  phone?: string
  email?: string
  company?: string
  address?: string
  notes?: string
}

export interface ProductCreate {
  project_id: string
  name: string
  category?: "home_cleaning" | "daily_goods" | "apparel_warmth" | "other"
  price_cny?: number
  specifications?: string
  selling_points?: string
  target_audience?: string
  usage_scenarios?: string
  proof_materials?: string
  image_url?: string
}

export interface ProductUpdate {
  name?: string
  category?: "home_cleaning" | "daily_goods" | "apparel_warmth" | "other"
  price_cny?: number
  specifications?: string
  selling_points?: string
  target_audience?: string
  usage_scenarios?: string
  proof_materials?: string
  image_url?: string
}

export interface CharacterCreate {
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
  is_core_ip?: boolean
}

export interface CharacterUpdate {
  name?: string
  gender?: "male" | "female" | "other"
  age_range?: string
  background?: string
  personality?: string
  catchphrases?: string
  worldview?: string
  commercial_boundary?: string
  reference_image_url?: string
  voice_reference_url?: string
  is_core_ip?: boolean
}

export interface StoryIdeaCreate {
  product_id: string
  title: string
  description?: string
  story_type?: string
  hook?: string
  conflict?: string
  twist?: string
  product_integration?: string
  score?: number
  status?: "generated" | "selected" | "rejected"
}

export interface StoryIdeaUpdate {
  title?: string
  description?: string
  story_type?: string
  hook?: string
  conflict?: string
  twist?: string
  product_integration?: string
  score?: number
  status?: "generated" | "selected" | "rejected"
}

export interface ScriptCreate {
  story_idea_id: string
  version?: number
  title: string
  content: string
  raw_ai_input?: string
  raw_ai_output?: string
  status?: "draft" | "approved" | "rejected" | "in_production"
  is_current?: boolean
}

export interface ScriptUpdate {
  title?: string
  content?: string
  raw_ai_input?: string
  raw_ai_output?: string
  status?: "draft" | "approved" | "rejected" | "in_production"
  is_current?: boolean
}

export interface StoryboardCreate {
  script_id: string
  shot_number: number
  description?: string
  image_prompt?: string
  dialogue?: string
  sound_effect?: string
  duration_seconds?: number
}

export interface StoryboardUpdate {
  description?: string
  image_prompt?: string
  dialogue?: string
  sound_effect?: string
  duration_seconds?: number
}

export interface ProductionTaskCreate {
  storyboard_id?: string
  task_type: string
  status?: "pending" | "in_progress" | "completed" | "failed"
  input_data?: string
  output_data?: string
  error_message?: string
  started_at?: string
  completed_at?: string
}

export interface ProductionTaskUpdate {
  status?: "pending" | "in_progress" | "completed" | "failed"
  input_data?: string
  output_data?: string
  error_message?: string
  started_at?: string
  completed_at?: string
}

export interface MediaAssetCreate {
  storyboard_id?: string
  production_task_id?: string
  media_type: "image" | "video" | "audio"
  file_path: string
  sha256?: string
  file_size_bytes?: number
  duration_seconds?: number
  width?: number
  height?: number
  ai_generated?: boolean
  ai_disclosure?: boolean
}

export interface MediaAssetUpdate {
  file_path?: string
  sha256?: string
  file_size_bytes?: number
  duration_seconds?: number
  width?: number
  height?: number
  ai_generated?: boolean
  ai_disclosure?: boolean
}

export interface AdvertisementCreate {
  project_id: string
  script_id?: string
  version?: number
  title: string
  file_path?: string
  sha256?: string
  duration_seconds?: number
  status?: "draft" | "reviewed" | "published" | "rejected"
  is_current?: boolean
  ai_disclosure?: boolean
}

export interface AdvertisementUpdate {
  title?: string
  file_path?: string
  sha256?: string
  duration_seconds?: number
  status?: "draft" | "reviewed" | "published" | "rejected"
  is_current?: boolean
  ai_disclosure?: boolean
}

export interface ComplianceReviewCreate {
  advertisement_id: string
  reviewer_type: string
  ai_disclosure_required?: boolean
  ai_disclosure_confirmed?: boolean
  product_authenticity?: boolean
  fictional_experience_check?: boolean
  portrait_authorization?: boolean
  voice_clone_authorization?: boolean
  music_license?: boolean
  trademark_check?: boolean
  ad_content_compliance?: boolean
  status?: "pending" | "passed" | "failed"
  remarks?: string
}

export interface ComplianceReviewUpdate {
  ai_disclosure_confirmed?: boolean
  product_authenticity?: boolean
  fictional_experience_check?: boolean
  portrait_authorization?: boolean
  voice_clone_authorization?: boolean
  music_license?: boolean
  trademark_check?: boolean
  ad_content_compliance?: boolean
  status?: "pending" | "passed" | "failed"
  remarks?: string
  reviewed_at?: string
}

export interface PublishingRecordCreate {
  advertisement_id: string
  platform?: "douyin" | "other"
  account_name?: string
  publish_url?: string
  publish_time?: string
  ai_disclosure_posted?: boolean
}

export interface PublishingRecordUpdate {
  account_name?: string
  publish_url?: string
  publish_time?: string
  ai_disclosure_posted?: boolean
}

export interface PerformanceMetricCreate {
  publishing_record_id: string
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

export interface PerformanceMetricUpdate {
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

export interface PromptTemplateCreate {
  name: string
  agent_type: string
  template_content: string
  variables?: string
  version?: number
  is_active?: boolean
}

export interface PromptTemplateUpdate {
  name?: string
  agent_type?: string
  template_content?: string
  variables?: string
  version?: number
  is_active?: boolean
}

export interface AuditLogCreate {
  user_id?: string
  action: string
  resource_type?: string
  resource_id?: string
  details?: string
  ip_address?: string
}
