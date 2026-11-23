"""CRUD classes for AI Story Commerce models"""

from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from app.crud import CRUDBase
from app.models import (
    Project, Product, Customer, Character, CharacterAsset,
    StoryIdea, Script, Storyboard, ProductionTask, MediaAsset,
    Advertisement, ComplianceReview, PublishingRecord, PerformanceMetric,
    PromptTemplate, AuditLog,
)
from app.schemas import (
    ProjectCreate, ProjectUpdate,
    CustomerCreate, CustomerUpdate,
    ProductCreate, ProductUpdate,
    CharacterCreate, CharacterUpdate,
    StoryIdeaCreate, StoryIdeaUpdate,
    ScriptCreate, ScriptUpdate,
    StoryboardCreate, StoryboardUpdate,
    ProductionTaskCreate, ProductionTaskUpdate,
    MediaAssetCreate, MediaAssetUpdate,
    AdvertisementCreate, AdvertisementUpdate,
    ComplianceReviewCreate, ComplianceReviewUpdate,
    PublishingRecordCreate, PublishingRecordUpdate,
    PerformanceMetricCreate, PerformanceMetricUpdate,
    PromptTemplateCreate, PromptTemplateUpdate,
    AuditLogCreate,
)


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Project]:
        result = await db.execute(select(Project).where(Project.name == name))
        return result.scalar_one_or_none()


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Customer]:
        result = await db.execute(select(Customer).where(Customer.name == name))
        return result.scalar_one_or_none()


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    async def get_by_project(
        self, db: AsyncSession, *, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        result = await db.execute(
            select(Product).where(Product.project_id == project_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class CRUDCharacter(CRUDBase[Character, CharacterCreate, CharacterUpdate]):
    async def get_core_ip(self, db: AsyncSession) -> Optional[Character]:
        result = await db.execute(select(Character).where(Character.is_core_ip == True))  # noqa: E712
        return result.scalar_one_or_none()


class CRUDStoryIdea(CRUDBase[StoryIdea, StoryIdeaCreate, StoryIdeaUpdate]):
    async def get_by_product(
        self, db: AsyncSession, *, product_id: str, skip: int = 0, limit: int = 100
    ) -> List[StoryIdea]:
        result = await db.execute(
            select(StoryIdea).where(StoryIdea.product_id == product_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class CRUDScript(CRUDBase[Script, ScriptCreate, ScriptUpdate]):
    async def get_by_story_idea(
        self, db: AsyncSession, *, story_idea_id: str, skip: int = 0, limit: int = 100
    ) -> List[Script]:
        result = await db.execute(
            select(Script).where(Script.story_idea_id == story_idea_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_current(self, db: AsyncSession, *, story_idea_id: str) -> Optional[Script]:
        result = await db.execute(
            select(Script).where(
                Script.story_idea_id == story_idea_id, Script.is_current == True  # noqa: E712
            )
        )
        return result.scalar_one_or_none()


class CRUDStoryboard(CRUDBase[Storyboard, StoryboardCreate, StoryboardUpdate]):
    async def get_by_script(
        self, db: AsyncSession, *, script_id: str, skip: int = 0, limit: int = 100
    ) -> List[Storyboard]:
        result = await db.execute(
            select(Storyboard).where(Storyboard.script_id == script_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class CRUDProductionTask(CRUDBase[ProductionTask, ProductionTaskCreate, ProductionTaskUpdate]):
    async def get_by_storyboard(
        self, db: AsyncSession, *, storyboard_id: str, skip: int = 0, limit: int = 100
    ) -> List[ProductionTask]:
        result = await db.execute(
            select(ProductionTask).where(ProductionTask.storyboard_id == storyboard_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class CRUDMediaAsset(CRUDBase[MediaAsset, MediaAssetCreate, MediaAssetUpdate]):
    async def get_by_storyboard(
        self, db: AsyncSession, *, storyboard_id: str, skip: int = 0, limit: int = 100
    ) -> List[MediaAsset]:
        result = await db.execute(
            select(MediaAsset).where(MediaAsset.storyboard_id == storyboard_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class CRUDAdvertisement(CRUDBase[Advertisement, AdvertisementCreate, AdvertisementUpdate]):
    async def get_by_project(
        self, db: AsyncSession, *, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[Advertisement]:
        result = await db.execute(
            select(Advertisement).where(Advertisement.project_id == project_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_current(self, db: AsyncSession, *, project_id: str) -> Optional[Advertisement]:
        result = await db.execute(
            select(Advertisement).where(
                Advertisement.project_id == project_id, Advertisement.is_current == True  # noqa: E712
            )
        )
        return result.scalar_one_or_none()


class CRUDComplianceReview(CRUDBase[ComplianceReview, ComplianceReviewCreate, ComplianceReviewUpdate]):
    async def get_by_advertisement(
        self, db: AsyncSession, *, advertisement_id: str, skip: int = 0, limit: int = 100
    ) -> List[ComplianceReview]:
        result = await db.execute(
            select(ComplianceReview).where(ComplianceReview.advertisement_id == advertisement_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class CRUDPublishingRecord(CRUDBase[PublishingRecord, PublishingRecordCreate, PublishingRecordUpdate]):
    async def get_by_advertisement(
        self, db: AsyncSession, *, advertisement_id: str, skip: int = 0, limit: int = 100
    ) -> List[PublishingRecord]:
        result = await db.execute(
            select(PublishingRecord).where(PublishingRecord.advertisement_id == advertisement_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class CRUDPerformanceMetric(CRUDBase[PerformanceMetric, PerformanceMetricCreate, PerformanceMetricUpdate]):
    async def get_by_publishing_record(
        self, db: AsyncSession, *, publishing_record_id: str, skip: int = 0, limit: int = 100
    ) -> List[PerformanceMetric]:
        result = await db.execute(
            select(PerformanceMetric).where(PerformanceMetric.publishing_record_id == publishing_record_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class CRUDPromptTemplate(CRUDBase[PromptTemplate, PromptTemplateCreate, PromptTemplateUpdate]):
    async def get_by_agent_type(
        self, db: AsyncSession, *, agent_type: str, skip: int = 0, limit: int = 100
    ) -> List[PromptTemplate]:
        result = await db.execute(
            select(PromptTemplate).where(PromptTemplate.agent_type == agent_type).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_active(self, db: AsyncSession, *, name: str) -> Optional[PromptTemplate]:
        result = await db.execute(
            select(PromptTemplate).where(PromptTemplate.name == name, PromptTemplate.is_active == True)  # noqa: E712
        )
        return result.scalar_one_or_none()


class CRUDAuditLog(CRUDBase[AuditLog, AuditLogCreate, Any]):
    async def get_recent(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit))
        return result.scalars().all()


# Instantiate CRUD objects
project = CRUDProject(Project)
customer = CRUDCustomer(Customer)
product = CRUDProduct(Product)
character = CRUDCharacter(Character)
character_asset = CRUDBase[CharacterAsset, Any, Any](CharacterAsset)
story_idea = CRUDStoryIdea(StoryIdea)
script = CRUDScript(Script)
storyboard = CRUDStoryboard(Storyboard)
production_task = CRUDProductionTask(ProductionTask)
media_asset = CRUDMediaAsset(MediaAsset)
advertisement = CRUDAdvertisement(Advertisement)
compliance_review = CRUDComplianceReview(ComplianceReview)
publishing_record = CRUDPublishingRecord(PublishingRecord)
performance_metric = CRUDPerformanceMetric(PerformanceMetric)
prompt_template = CRUDPromptTemplate(PromptTemplate)
audit_log = CRUDAuditLog(AuditLog)

__all__ = [
    "project", "customer", "product", "character", "character_asset",
    "story_idea", "script", "storyboard", "production_task", "media_asset",
    "advertisement", "compliance_review", "publishing_record", "performance_metric",
    "prompt_template", "audit_log",
]
