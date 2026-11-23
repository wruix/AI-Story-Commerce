"""Pydantic schemas for AI Story Commerce backend"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
class ProjectBase(BaseSchema):
    name: str
    description: Optional[str] = None
    customer_id: Optional[str] = None
    budget_cny: Optional[float] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    customer_id: Optional[str] = None
    budget_cny: Optional[float] = None


class ProjectOut(ProjectBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------
class CustomerBase(BaseSchema):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseSchema):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerOut(CustomerBase):
    id: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
class ProductBase(BaseSchema):
    project_id: str
    name: str
    category: str = "other"
    price_cny: Optional[float] = None
    specifications: Optional[str] = None
    selling_points: Optional[str] = None
    target_audience: Optional[str] = None
    usage_scenarios: Optional[str] = None
    proof_materials: Optional[str] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseSchema):
    name: Optional[str] = None
    category: Optional[str] = None
    price_cny: Optional[float] = None
    specifications: Optional[str] = None
    selling_points: Optional[str] = None
    target_audience: Optional[str] = None
    usage_scenarios: Optional[str] = None
    proof_materials: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------
class CharacterBase(BaseSchema):
    name: str
    gender: str
    age_range: Optional[str] = None
    background: Optional[str] = None
    personality: Optional[str] = None
    catchphrases: Optional[str] = None
    worldview: Optional[str] = None
    commercial_boundary: Optional[str] = None
    reference_image_url: Optional[str] = None
    voice_reference_url: Optional[str] = None
    is_core_ip: bool = False


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseSchema):
    name: Optional[str] = None
    gender: Optional[str] = None
    age_range: Optional[str] = None
    background: Optional[str] = None
    personality: Optional[str] = None
    catchphrases: Optional[str] = None
    worldview: Optional[str] = None
    commercial_boundary: Optional[str] = None
    reference_image_url: Optional[str] = None
    voice_reference_url: Optional[str] = None
    is_core_ip: Optional[bool] = None


class CharacterOut(CharacterBase):
    id: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Story Ideas
# ---------------------------------------------------------------------------
class StoryIdeaBase(BaseSchema):
    product_id: str
    title: str
    description: Optional[str] = None
    story_type: Optional[str] = None
    hook: Optional[str] = None
    conflict: Optional[str] = None
    twist: Optional[str] = None
    product_integration: Optional[str] = None
    score: Optional[float] = None
    status: str = "generated"


class StoryIdeaCreate(StoryIdeaBase):
    pass


class StoryIdeaUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    story_type: Optional[str] = None
    hook: Optional[str] = None
    conflict: Optional[str] = None
    twist: Optional[str] = None
    product_integration: Optional[str] = None
    score: Optional[float] = None
    status: Optional[str] = None


class StoryIdeaOut(StoryIdeaBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Scripts
# ---------------------------------------------------------------------------
class ScriptBase(BaseSchema):
    story_idea_id: str
    version: int = 1
    title: str
    content: str
    raw_ai_input: Optional[str] = None
    raw_ai_output: Optional[str] = None
    status: str = "draft"
    is_current: bool = True


class ScriptCreate(ScriptBase):
    pass


class ScriptUpdate(BaseSchema):
    title: Optional[str] = None
    content: Optional[str] = None
    raw_ai_input: Optional[str] = None
    raw_ai_output: Optional[str] = None
    status: Optional[str] = None
    is_current: Optional[bool] = None


class ScriptOut(ScriptBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Storyboards
# ---------------------------------------------------------------------------
class StoryboardBase(BaseSchema):
    script_id: str
    shot_number: int
    description: Optional[str] = None
    image_prompt: Optional[str] = None
    dialogue: Optional[str] = None
    sound_effect: Optional[str] = None
    duration_seconds: Optional[float] = None


class StoryboardCreate(StoryboardBase):
    pass


class StoryboardUpdate(BaseSchema):
    description: Optional[str] = None
    image_prompt: Optional[str] = None
    dialogue: Optional[str] = None
    sound_effect: Optional[str] = None
    duration_seconds: Optional[float] = None


class StoryboardOut(StoryboardBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Production Tasks
# ---------------------------------------------------------------------------
class ProductionTaskBase(BaseSchema):
    storyboard_id: Optional[str] = None
    task_type: str
    status: str = "pending"
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None


class ProductionTaskCreate(ProductionTaskBase):
    pass


class ProductionTaskUpdate(BaseSchema):
    status: Optional[str] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProductionTaskOut(ProductionTaskBase):
    id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Media Assets
# ---------------------------------------------------------------------------
class MediaAssetBase(BaseSchema):
    storyboard_id: Optional[str] = None
    production_task_id: Optional[str] = None
    media_type: str
    file_path: str
    sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    ai_generated: bool = False
    ai_disclosure: bool = False


class MediaAssetCreate(MediaAssetBase):
    pass


class MediaAssetUpdate(BaseSchema):
    file_path: Optional[str] = None
    sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    ai_generated: Optional[bool] = None
    ai_disclosure: Optional[bool] = None


class MediaAssetOut(MediaAssetBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Advertisements
# ---------------------------------------------------------------------------
class AdvertisementBase(BaseSchema):
    project_id: str
    script_id: Optional[str] = None
    version: int = 1
    title: str
    file_path: Optional[str] = None
    sha256: Optional[str] = None
    duration_seconds: Optional[float] = None
    status: str = "draft"
    is_current: bool = True
    ai_disclosure: bool = False


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseSchema):
    title: Optional[str] = None
    file_path: Optional[str] = None
    sha256: Optional[str] = None
    duration_seconds: Optional[float] = None
    status: Optional[str] = None
    is_current: Optional[bool] = None
    ai_disclosure: Optional[bool] = None


class AdvertisementOut(AdvertisementBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Compliance Reviews
# ---------------------------------------------------------------------------
class ComplianceReviewBase(BaseSchema):
    advertisement_id: str
    reviewer_type: str
    ai_disclosure_required: bool = True
    ai_disclosure_confirmed: bool = False
    product_authenticity: Optional[bool] = None
    fictional_experience_check: Optional[bool] = None
    portrait_authorization: Optional[bool] = None
    voice_clone_authorization: Optional[bool] = None
    music_license: Optional[bool] = None
    trademark_check: Optional[bool] = None
    ad_content_compliance: Optional[bool] = None
    status: str = "pending"
    remarks: Optional[str] = None


class ComplianceReviewCreate(ComplianceReviewBase):
    pass


class ComplianceReviewUpdate(BaseSchema):
    ai_disclosure_confirmed: Optional[bool] = None
    product_authenticity: Optional[bool] = None
    fictional_experience_check: Optional[bool] = None
    portrait_authorization: Optional[bool] = None
    voice_clone_authorization: Optional[bool] = None
    music_license: Optional[bool] = None
    trademark_check: Optional[bool] = None
    ad_content_compliance: Optional[bool] = None
    status: Optional[str] = None
    remarks: Optional[str] = None
    reviewed_at: Optional[datetime] = None


class ComplianceReviewOut(ComplianceReviewBase):
    id: str
    reviewed_at: Optional[datetime] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Publishing Records
# ---------------------------------------------------------------------------
class PublishingRecordBase(BaseSchema):
    advertisement_id: str
    platform: str = "douyin"
    account_name: Optional[str] = None
    publish_url: Optional[str] = None
    publish_time: Optional[datetime] = None
    ai_disclosure_posted: bool = False


class PublishingRecordCreate(PublishingRecordBase):
    pass


class PublishingRecordUpdate(BaseSchema):
    account_name: Optional[str] = None
    publish_url: Optional[str] = None
    publish_time: Optional[datetime] = None
    ai_disclosure_posted: Optional[bool] = None


class PublishingRecordOut(PublishingRecordBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Performance Metrics
# ---------------------------------------------------------------------------
class PerformanceMetricBase(BaseSchema):
    publishing_record_id: str
    views: Optional[int] = None
    completion_rate: Optional[float] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    product_clicks: Optional[int] = None
    orders: Optional[int] = None
    cost_cny: Optional[float] = None
    cpa_cny: Optional[float] = None
    roas: Optional[float] = None


class PerformanceMetricCreate(PerformanceMetricBase):
    pass


class PerformanceMetricUpdate(BaseSchema):
    views: Optional[int] = None
    completion_rate: Optional[float] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    product_clicks: Optional[int] = None
    orders: Optional[int] = None
    cost_cny: Optional[float] = None
    cpa_cny: Optional[float] = None
    roas: Optional[float] = None


class PerformanceMetricOut(PerformanceMetricBase):
    id: str
    recorded_at: datetime


# ---------------------------------------------------------------------------
# Prompt Templates
# ---------------------------------------------------------------------------
class PromptTemplateBase(BaseSchema):
    name: str
    agent_type: str
    template_content: str
    variables: Optional[str] = None
    version: int = 1
    is_active: bool = True


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseSchema):
    name: Optional[str] = None
    agent_type: Optional[str] = None
    template_content: Optional[str] = None
    variables: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None


class PromptTemplateOut(PromptTemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------
class AuditLogBase(BaseSchema):
    user_id: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogOut(AuditLogBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
class HealthOut(BaseSchema):
    status: str
    service: str
    version: str
