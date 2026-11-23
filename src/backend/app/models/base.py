"""AI Story Commerce — SQLAlchemy Models

Core tables (14+):
1. projects - 商业项目
2. products - 商品资料
3. customers - 商家客户
4. characters - 虚拟人物
5. character_assets - 人物参考素材
6. story_ideas - 剧情创意
7. scripts - 剧本版本
8. storyboards - 分镜
9. production_tasks - 视频生产任务
10. media_assets - 图片、视频、音频
11. advertisements - 广告成片
12. compliance_reviews - 合规审核
13. publishing_records - 发布记录
14. performance_metrics - 广告数据
15. prompt_templates - AI提示词模板
16. audit_logs - 操作审计

Relationships:
- 一个项目可有多个商品
- 一个商品可有多个剧情创意
- 一个剧情创意可有多个剧本版本
- 一个剧本可关联多个角色（多对多）
- 一个剧本可生成多个分镜
- 一个分镜可产生多个视频素材
- 一个广告可有多个发布记录
- 一个发布记录可关联多组效果数据

Version rule: scripts and advertisements keep version history, never overwrite.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import (
    String, Text, Integer, DateTime, ForeignKey, Boolean,
    Enum, Float, JSON, Table, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.sqlite import BLOB


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Association table: scripts <-> characters (many-to-many)
script_characters = Table(
    "script_characters",
    Base.metadata,
    Column("script_id", ForeignKey("scripts.id", ondelete="CASCADE"), primary_key=True),
    Column("character_id", ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
)


class ProjectStatus(str, PyEnum):
    draft = "draft"
    active = "active"
    completed = "completed"
    archived = "archived"


class ProductCategory(str, PyEnum):
    home_cleaning = "home_cleaning"
    daily_goods = "daily_goods"
    apparel_warmth = "apparel_warmth"
    other = "other"


class StoryIdeaStatus(str, PyEnum):
    generated = "generated"
    selected = "selected"
    rejected = "rejected"


class ScriptStatus(str, PyEnum):
    draft = "draft"
    approved = "approved"
    rejected = "rejected"
    in_production = "in_production"


class CharacterGender(str, PyEnum):
    male = "male"
    female = "female"
    other = "other"


class TaskStatus(str, PyEnum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class MediaType(str, PyEnum):
    image = "image"
    video = "video"
    audio = "audio"


class AdStatus(str, PyEnum):
    draft = "draft"
    reviewed = "reviewed"
    published = "published"
    rejected = "rejected"


class ComplianceStatus(str, PyEnum):
    pending = "pending"
    passed = "passed"
    failed = "failed"


class PublishPlatform(str, PyEnum):
    douyin = "douyin"
    other = "other"


# ---------------------------------------------------------------------------
# 1. projects - 商业项目
# ---------------------------------------------------------------------------
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.draft, nullable=False)
    customer_id: Mapped[Optional[str]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    budget_cny: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship(back_populates="projects")
    products: Mapped[List["Product"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    advertisements: Mapped[List["Advertisement"]] = relationship(back_populates="project", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 2. products - 商品资料
# ---------------------------------------------------------------------------
class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory), default=ProductCategory.other, nullable=False)
    price_cny: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    specifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    selling_points: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    usage_scenarios: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proof_materials: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 真实证明材料
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="products")
    story_ideas: Mapped[List["StoryIdea"]] = relationship(back_populates="product", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 3. customers - 商家客户
# ---------------------------------------------------------------------------
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    projects: Mapped[List["Project"]] = relationship(back_populates="customer")


# ---------------------------------------------------------------------------
# 4. characters - 虚拟人物
# ---------------------------------------------------------------------------
class Character(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    gender: Mapped[CharacterGender] = mapped_column(Enum(CharacterGender), nullable=False)
    age_range: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    background: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personality: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    catchphrases: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 口头禅
    worldview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 世界观
    commercial_boundary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 商业合作边界
    reference_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    voice_reference_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_core_ip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    scripts: Mapped[List["Script"]] = relationship(secondary=script_characters, back_populates="characters")
    assets: Mapped[List["CharacterAsset"]] = relationship(back_populates="character", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 5. character_assets - 人物参考素材
# ---------------------------------------------------------------------------
class CharacterAsset(Base):
    __tablename__ = "character_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)  # front, side, full_body, etc.
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    character: Mapped["Character"] = relationship(back_populates="assets")


# ---------------------------------------------------------------------------
# 6. story_ideas - 剧情创意
# ---------------------------------------------------------------------------
class StoryIdea(Base):
    __tablename__ = "story_ideas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    story_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 误会型、反转型等
    hook: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 前3秒钩子
    conflict: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 冲突
    twist: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 反转
    product_integration: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 商品植入
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 剧情评分
    status: Mapped[StoryIdeaStatus] = mapped_column(Enum(StoryIdeaStatus), default=StoryIdeaStatus.generated, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="story_ideas")
    scripts: Mapped[List["Script"]] = relationship(back_populates="story_idea", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 7. scripts - 剧本版本
# ---------------------------------------------------------------------------
class Script(Base):
    __tablename__ = "scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_idea_id: Mapped[str] = mapped_column(ForeignKey("story_ideas.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 完整剧本内容
    raw_ai_input: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI原始输入
    raw_ai_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI原始输出
    status: Mapped[ScriptStatus] = mapped_column(Enum(ScriptStatus), default=ScriptStatus.draft, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # 是否当前版本
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    story_idea: Mapped["StoryIdea"] = relationship(back_populates="scripts")
    characters: Mapped[List["Character"]] = relationship(secondary=script_characters, back_populates="scripts")
    storyboards: Mapped[List["Storyboard"]] = relationship(back_populates="script", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 8. storyboards - 分镜
# ---------------------------------------------------------------------------
class Storyboard(Base):
    __tablename__ = "storyboards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    script_id: Mapped[str] = mapped_column(ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False, index=True)
    shot_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 镜头号
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 镜头描述
    image_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 画面提示词
    dialogue: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 对白
    sound_effect: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 音效
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    script: Mapped["Script"] = relationship(back_populates="storyboards")
    media_assets: Mapped[List["MediaAsset"]] = relationship(back_populates="storyboard", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 9. production_tasks - 视频生产任务
# ---------------------------------------------------------------------------
class ProductionTask(Base):
    __tablename__ = "production_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    storyboard_id: Mapped[Optional[str]] = mapped_column(ForeignKey("storyboards.id", ondelete="SET NULL"), nullable=True, index=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)  # image_gen, video_gen, voice, edit
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.pending, nullable=False)
    input_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 任务输入数据(JSON)
    output_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 任务输出数据(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    storyboard: Mapped[Optional["Storyboard"]] = relationship(back_populates="production_tasks")


# Add back relationship to Storyboard
Storyboard.production_tasks = relationship("ProductionTask", back_populates="storyboard", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 10. media_assets - 图片、视频、音频
# ---------------------------------------------------------------------------
class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    storyboard_id: Mapped[Optional[str]] = mapped_column(ForeignKey("storyboards.id", ondelete="SET NULL"), nullable=True, index=True)
    production_task_id: Mapped[Optional[str]] = mapped_column(ForeignKey("production_tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_disclosure: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # AI内容标识
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    storyboard: Mapped[Optional["Storyboard"]] = relationship(back_populates="media_assets")
    production_task: Mapped[Optional["ProductionTask"]] = relationship(back_populates="media_assets")


ProductionTask.media_assets = relationship("MediaAsset", back_populates="production_task", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 11. advertisements - 广告成片
# ---------------------------------------------------------------------------
class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    script_id: Mapped[Optional[str]] = mapped_column(ForeignKey("scripts.id", ondelete="SET NULL"), nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 成片文件路径
    sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[AdStatus] = mapped_column(Enum(AdStatus), default=AdStatus.draft, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_disclosure: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="advertisements")
    script: Mapped[Optional["Script"]] = relationship()
    publishing_records: Mapped[List["PublishingRecord"]] = relationship(back_populates="advertisement", cascade="all, delete-orphan")
    compliance_reviews: Mapped[List["ComplianceReview"]] = relationship(back_populates="advertisement", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 12. compliance_reviews - 合规审核
# ---------------------------------------------------------------------------
class ComplianceReview(Base):
    __tablename__ = "compliance_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    advertisement_id: Mapped[str] = mapped_column(ForeignKey("advertisements.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_type: Mapped[str] = mapped_column(String(50), nullable=False)  # agent 或 human
    ai_disclosure_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_disclosure_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    product_authenticity: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    fictional_experience_check: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    portrait_authorization: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    voice_clone_authorization: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    music_license: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    trademark_check: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    ad_content_compliance: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    status: Mapped[ComplianceStatus] = mapped_column(Enum(ComplianceStatus), default=ComplianceStatus.pending, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    advertisement: Mapped["Advertisement"] = relationship(back_populates="compliance_reviews")


# ---------------------------------------------------------------------------
# 13. publishing_records - 发布记录
# ---------------------------------------------------------------------------
class PublishingRecord(Base):
    __tablename__ = "publishing_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    advertisement_id: Mapped[str] = mapped_column(ForeignKey("advertisements.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[PublishPlatform] = mapped_column(Enum(PublishPlatform), default=PublishPlatform.douyin, nullable=False)
    account_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    publish_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    publish_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ai_disclosure_posted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 用户主动声明
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    advertisement: Mapped["Advertisement"] = relationship(back_populates="publishing_records")
    performance_metrics: Mapped[List["PerformanceMetric"]] = relationship(back_populates="publishing_record", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 14. performance_metrics - 广告数据
# ---------------------------------------------------------------------------
class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    publishing_record_id: Mapped[str] = mapped_column(ForeignKey("publishing_records.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 完播率
    likes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shares: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    product_clicks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 商品点击
    orders: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 订单数
    cost_cny: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 广告成本
    cpa_cny: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 每获客成本
    roas: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 广告支出回报率

    # Relationships
    publishing_record: Mapped["PublishingRecord"] = relationship(back_populates="performance_metrics")


# ---------------------------------------------------------------------------
# 15. prompt_templates - AI提示词模板
# ---------------------------------------------------------------------------
class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # product_research, creative_director, etc.
    template_content: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 变量列表
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ---------------------------------------------------------------------------
# 16. audit_logs - 操作审计
# ---------------------------------------------------------------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 操作详情
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


# Indexes for common queries
Index("ix_products_project_id", Product.project_id)
Index("ix_story_ideas_product_id", StoryIdea.product_id)
Index("ix_scripts_story_idea_id", Script.story_idea_id)
Index("ix_storyboards_script_id", Storyboard.script_id)
Index("ix_media_assets_storyboard_id", MediaAsset.storyboard_id)
Index("ix_advertisements_project_id", Advertisement.project_id)
Index("ix_compliance_reviews_ad_id", ComplianceReview.advertisement_id)
Index("ix_publishing_records_ad_id", PublishingRecord.advertisement_id)
Index("ix_performance_metrics_publish_id", PerformanceMetric.publishing_record_id)
